"""FastAPI Application – Haupteinstiegspunkt."""

import base64
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from botbuilder.core import CardFactory, TurnContext
from botbuilder.schema import Activity, Attachment, ConversationReference
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.input_processor import (
    build_manus_prompt,
    classify_input,
    extract_fields,
    validate_fields,
)
from app.manus.client import ManusClient
from app.manus.schemas import WebhookEvent
from app.manus.webhook_handler import handle_manus_webhook
from app.models.task import AnalysisTask, TaskStatus
from app.teams.messages import adapter, bot

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialisiere Datenbank...")
    init_db()
    logger.info("SalesBot Backend gestartet (env=%s)", settings.environment)
    yield
    logger.info("SalesBot Backend heruntergefahren.")


app = FastAPI(
    title="SalesBot – Automatisierte KI-Analysen",
    description="Teams-Bot Backend für Wettbewerbsanalysen via Manus.ai",
    version="0.2.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Briefing-Endpoint (HTTP-Test-Schnittstelle)
# ---------------------------------------------------------------------------
class BriefingRequest(BaseModel):
    text: str
    user_id: str = "test-user"
    user_name: str = "Test User"


class BriefingResponse(BaseModel):
    message: str
    task_id: int | None = None
    manus_task_id: str | None = None
    manus_prompt: str | None = None
    status: str = "pending"


@app.post("/api/briefing", response_model=BriefingResponse)
async def create_briefing(
    request: BriefingRequest, db: Session = Depends(get_db)
):
    """Nimmt ein Briefing entgegen, normalisiert es und schickt es an Manus."""
    modus = classify_input(request.text)
    extraction = await extract_fields(request.text, modus)
    validation = validate_fields(extraction)

    if not validation.is_valid:
        return BriefingResponse(
            message=validation.reply_message or "Eingabe unvollständig.",
            status="needs_input",
        )

    manus_prompt = build_manus_prompt(extraction)

    task = AnalysisTask(
        unternehmen=extraction.unternehmen,
        standort=extraction.standort,
        position=extraction.position,
        zusatzkontext=extraction.zusatzkontext,
        manus_prompt=manus_prompt,
        input_modus=modus.value,
        teams_user_id=request.user_id,
        teams_user_name=request.user_name,
        status=TaskStatus.PROCESSING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        manus_client = ManusClient()
        manus_response = await manus_client.create_task(manus_prompt)
        task.manus_task_id = manus_response.task_id
        db.commit()
    except Exception as e:
        logger.error("Manus API Fehler: %s", e)
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        db.commit()
        return BriefingResponse(
            message=f"Manus API Fehler: {e}",
            task_id=task.id,
            status="failed",
        )

    return BriefingResponse(
        message=validation.reply_message or "Wettbewerbsanalyse wird erstellt...",
        task_id=task.id,
        manus_task_id=manus_response.task_id,
        manus_prompt=manus_prompt,
        status="processing",
    )


# ---------------------------------------------------------------------------
# Manus Webhook
# ---------------------------------------------------------------------------
@app.post("/api/manus/webhook")
async def manus_webhook(request: Request, db: Session = Depends(get_db)):
    """Empfängt Webhook-Events von Manus und liefert Ergebnisse an Teams."""
    body = await request.json()
    logger.info("Manus webhook empfangen: %s", body.get("event_type", "unknown"))

    event = WebhookEvent(**body)

    task = await handle_manus_webhook(event, db)
    if not task:
        return {"status": "ok", "detail": "Task nicht in DB (ggf. test event)"}

    if task.status == TaskStatus.COMPLETED and task.conversation_reference:
        try:
            await _send_result_to_teams(task)
            logger.info(
                "Präsentation an %s gesendet (Task %s)",
                task.teams_user_name,
                task.id,
            )
        except Exception as e:
            logger.error("Fehler beim Senden an Teams: %s", e, exc_info=True)

    return {"status": "ok", "task_id": task.id, "task_status": task.status.value}


async def _send_result_to_teams(task: AnalysisTask):
    """Lädt die Präsentation von Manus herunter und sendet sie proaktiv an Teams."""
    conv_ref_data = json.loads(task.conversation_reference)
    conv_ref = ConversationReference().deserialize(conv_ref_data)

    file_name = task.result_file_name or "Wettbewerbsanalyse.pptx"

    if task.result_file_url:
        manus_client = ManusClient()
        file_bytes = await manus_client.download_artifact(task.result_file_url)

        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        content_type = _guess_content_type(file_name)

        attachment = Attachment(
            name=file_name,
            content_type=content_type,
            content_url=f"data:{content_type};base64,{file_b64}",
        )

        async def send_file(turn_context: TurnContext):
            reply = Activity(
                type="message",
                text=f"Die Wettbewerbsanalyse für **{task.unternehmen}** ist fertig!",
                attachments=[attachment],
            )
            await turn_context.send_activity(reply)

        await adapter.continue_conversation(conv_ref, send_file, settings.microsoft_app_id)
    else:
        async def send_notice(turn_context: TurnContext):
            await turn_context.send_activity(
                f"Die Wettbewerbsanalyse für **{task.unternehmen}** ist fertig!\n\n"
                "Leider konnte keine Datei heruntergeladen werden."
            )

        await adapter.continue_conversation(conv_ref, send_notice, settings.microsoft_app_id)


def _guess_content_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "zip": "application/zip",
    }.get(ext, "application/octet-stream")


# ---------------------------------------------------------------------------
# Teams Bot Messaging Endpoint
# ---------------------------------------------------------------------------
@app.post("/api/teams/messages")
async def teams_messages(request: Request):
    """Empfängt Nachrichten vom Bot Framework (Teams)."""
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return response
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Task-Status (Debug)
# ---------------------------------------------------------------------------
@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Task-Status abfragen (für Debugging und Monitoring)."""
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")

    return {
        "id": task.id,
        "unternehmen": task.unternehmen,
        "standort": task.standort,
        "position": task.position,
        "status": task.status.value,
        "manus_task_id": task.manus_task_id,
        "result_file_url": task.result_file_url,
        "result_file_name": task.result_file_name,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }

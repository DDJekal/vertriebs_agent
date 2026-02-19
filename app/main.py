"""FastAPI Application – Haupteinstiegspunkt."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from botbuilder.schema import Activity
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
    version="0.1.0",
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
# Briefing-Endpoint (HTTP-Test-Schnittstelle, bis Teams-Bot steht)
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
    """Nimmt ein Briefing entgegen, normalisiert es und schickt es an Manus.

    Dieser Endpoint dient als Test-Schnittstelle (alternativ zum Teams-Bot).
    """
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
    """Empfängt Webhook-Events von Manus (task_stopped, task_progress)."""
    body = await request.json()
    event = WebhookEvent(**body)

    task = await handle_manus_webhook(event, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")

    if task.status == TaskStatus.COMPLETED and task.teams_user_id:
        logger.info(
            "Task %s abgeschlossen – Benachrichtigung an %s",
            task.id,
            task.teams_user_name,
        )

    return {"status": "ok", "task_id": task.id, "task_status": task.status.value}


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
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }

"""Slack Message Handler – verarbeitet eingehende Nachrichten."""

import logging
from sqlalchemy.orm import Session

from app.input_processor import (
    build_manus_prompt,
    classify_input,
    extract_fields,
    validate_fields,
)
from app.manus.client import ManusClient
from app.models.task import AnalysisTask, TaskStatus

logger = logging.getLogger(__name__)


async def handle_slack_message(event: dict, say, db: Session):
    """Verarbeitet eine eingehende Slack-Nachricht.
    
    Args:
        event: Slack Event-Dict mit text, user, channel, etc.
        say: Slack say() Funktion zum Antworten
        db: SQLAlchemy Session
    """
    text = event.get("text", "").strip()
    user_id = event.get("user", "")
    channel_id = event.get("channel", "")
    
    if not text:
        await say("Bitte sende ein Briefing mit Unternehmen, Position und Standort.")
        return
    
    if text.lower() in ("hilfe", "help", "?"):
        await say(_help_text())
        return
    
    modus = classify_input(text)
    extraction = await extract_fields(text, modus)
    validation = validate_fields(extraction)
    
    if not validation.is_valid:
        await say(validation.reply_message)
        return
    
    manus_prompt = build_manus_prompt(extraction)
    
    task = AnalysisTask(
        unternehmen=extraction.unternehmen,
        standort=extraction.standort,
        position=extraction.position,
        zusatzkontext=extraction.zusatzkontext,
        manus_prompt=manus_prompt,
        input_modus=modus.value,
        source_platform="slack",
        slack_channel_id=channel_id,
        slack_user_id=user_id,
        status=TaskStatus.PROCESSING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    await say(validation.reply_message)
    
    try:
        manus_client = ManusClient()
        manus_response = await manus_client.create_task(manus_prompt)
        task.manus_task_id = manus_response.task_id
        db.commit()
        logger.info(
            "Manus task %s erstellt für %s (DB task %s, Slack)",
            manus_response.task_id,
            extraction.unternehmen,
            task.id,
        )
    except Exception as e:
        logger.error("Manus API Fehler: %s", e)
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        db.commit()
        await say(f"Fehler bei der Manus-API: {e}\nBitte versuche es erneut.")


def _help_text() -> str:
    return (
        "*SalesBot – Wettbewerbsanalyse*\n\n"
        "Schicke mir ein Briefing in einem der folgenden Formate:\n\n"
        "*Kurzformat:*\n"
        "```\nDRK Kreisverband Lausitz e.V.\nHEP\nLausitz\n```\n\n"
        "*Ausführlich (mit Pain Points):*\n"
        "```\nDRK Kreisverband Lausitz e.V.\n2-3 HEPs, Lausitz\n"
        "Rentenwelle, Agenturversagen, Ghosting...\n```\n\n"
        "*Strukturiert:*\n"
        "```\n*Unternehmen:* Name\n*Standort:* Stadt\n"
        "*Position:* Berufsbezeichnung\n```\n\n"
        "Ich extrahiere die Daten, erstelle einen Manus-Auftrag "
        "und schicke dir die fertige Präsentation."
    )

"""Verarbeitet eingehende Webhooks von Manus (task_stopped etc.)."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.manus.schemas import WebhookAttachment, WebhookEvent
from app.models.task import AnalysisTask, TaskStatus

_PREFERRED_EXTENSIONS = (".pdf", ".pptx", ".html", ".docx", ".xlsx")


def _pick_best_attachment(attachments: list[WebhookAttachment]) -> WebhookAttachment:
    """Waehlt das beste Attachment: PDF > PPTX > HTML > Rest. Ignoriert slides.json."""
    for ext in _PREFERRED_EXTENSIONS:
        for att in attachments:
            if att.file_name.lower().endswith(ext):
                return att
    for att in attachments:
        if not att.file_name.lower().endswith(".json"):
            return att
    return attachments[0]

logger = logging.getLogger(__name__)


async def handle_manus_webhook(event: WebhookEvent, db: Session) -> AnalysisTask | None:
    """Verarbeitet ein Manus-Webhook-Event und aktualisiert den Task in der DB.

    Returns:
        Den aktualisierten Task oder None wenn nicht gefunden.
    """
    task_id = event.task_id
    if not task_id:
        logger.warning("Webhook ohne task_id empfangen: %s", event.event_id)
        return None

    task = (
        db.query(AnalysisTask)
        .filter(AnalysisTask.manus_task_id == task_id)
        .first()
    )

    if not task:
        logger.warning("Webhook für unbekannten Task: %s", task_id)
        return None

    if event.event_type == "task_stopped" and event.task_detail:
        detail = event.task_detail

        if detail.stop_reason == "finish":
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            logger.info("Manus task completed: %s", task_id)

            if detail.attachments:
                preferred = _pick_best_attachment(detail.attachments)
                task.result_file_url = preferred.url
                task.result_file_name = preferred.file_name

            if detail.task_url:
                task.manus_task_url = detail.task_url

        elif detail.stop_reason == "ask":
            logger.info("Manus task wartet auf Input: %s – %s", task_id, detail.message)

        else:
            task.status = TaskStatus.FAILED
            task.error_message = detail.message or "Unbekannter Stop-Grund"
            logger.error("Manus task stopped unexpectedly: %s", task_id)

    elif event.event_type == "task_progress" and event.progress_detail:
        logger.info(
            "Manus task progress: %s – %s",
            task_id,
            event.progress_detail.message,
        )

    elif event.event_type == "task_created":
        logger.info("Manus task created webhook: %s", task_id)

    db.commit()
    db.refresh(task)
    return task

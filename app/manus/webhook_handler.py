"""Verarbeitet eingehende Webhooks von Manus (task_stopped etc.)."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.manus.schemas import WebhookEvent
from app.models.task import AnalysisTask, TaskStatus

logger = logging.getLogger(__name__)


async def handle_manus_webhook(event: WebhookEvent, db: Session) -> AnalysisTask | None:
    """Verarbeitet ein Manus-Webhook-Event und aktualisiert den Task in der DB.

    Returns:
        Den aktualisierten Task oder None wenn nicht gefunden.
    """
    task = (
        db.query(AnalysisTask)
        .filter(AnalysisTask.manus_task_id == event.task_id)
        .first()
    )

    if not task:
        logger.warning("Webhook für unbekannten Task: %s", event.task_id)
        return None

    if event.event_type == "task_stopped":
        if event.error:
            task.status = TaskStatus.FAILED
            task.error_message = event.error
            logger.error("Manus task failed: %s – %s", event.task_id, event.error)
        else:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            logger.info("Manus task completed: %s", event.task_id)

            if event.artifacts:
                file_urls = [
                    a.get("url") for a in event.artifacts if a.get("url")
                ]
                if file_urls:
                    task.result_file_url = file_urls[0]

    elif event.event_type == "task_progress":
        logger.info("Manus task progress: %s", event.task_id)

    db.commit()
    db.refresh(task)
    return task

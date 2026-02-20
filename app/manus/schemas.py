"""Pydantic-Modelle für die Manus API Request/Response-Objekte."""

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    prompt: str
    project_id: str | None = None
    task_mode: str = "agent"


class TaskResponse(BaseModel):
    task_id: str
    status: str = ""
    output: str | None = None
    artifacts: list[dict] | None = None


# ---------------------------------------------------------------------------
# Webhook-Modelle (basierend auf https://open.manus.ai/docs/webhooks)
# ---------------------------------------------------------------------------


class WebhookAttachment(BaseModel):
    file_name: str
    url: str
    size_bytes: int = 0


class WebhookTaskDetail(BaseModel):
    task_id: str
    task_title: str = ""
    task_url: str = ""
    message: str = ""
    attachments: list[WebhookAttachment] = []
    stop_reason: str = ""


class WebhookProgressDetail(BaseModel):
    task_id: str
    progress_type: str = ""
    message: str = ""


class WebhookEvent(BaseModel):
    event_id: str = ""
    event_type: str
    task_detail: WebhookTaskDetail | None = None
    progress_detail: WebhookProgressDetail | None = None

    @property
    def task_id(self) -> str | None:
        if self.task_detail:
            return self.task_detail.task_id
        if self.progress_detail:
            return self.progress_detail.task_id
        return None

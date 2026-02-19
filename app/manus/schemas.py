"""Pydantic-Modelle für die Manus API Request/Response-Objekte."""

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    prompt: str
    project_id: str | None = None
    task_mode: str = "agent"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    output: str | None = None
    artifacts: list[dict] | None = None


class WebhookEvent(BaseModel):
    event_type: str
    task_id: str
    status: str | None = None
    output: str | None = None
    artifacts: list[dict] | None = None
    error: str | None = None

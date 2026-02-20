"""HTTP-Client für die Manus REST-API."""

import logging

import httpx

from app.config import settings
from app.manus.schemas import CreateTaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class ManusClient:
    def __init__(self):
        self.base_url = settings.manus_api_base_url.rstrip("/")
        self.api_key = settings.manus_api_key
        self.project_id = settings.manus_project_id or None

    def _headers(self) -> dict[str, str]:
        return {
            "API_KEY": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_task(self, prompt: str) -> TaskResponse:
        """Erstellt einen neuen Task in Manus."""
        request = CreateTaskRequest(
            prompt=prompt,
            project_id=self.project_id,
            task_mode="agent",
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/tasks",
                headers=self._headers(),
                json=request.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            data = response.json()

        logger.info("Manus task created: %s", data.get("task_id"))
        return TaskResponse(**data)

    async def get_task(self, task_id: str) -> TaskResponse:
        """Fragt den Status eines Tasks ab."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

        return TaskResponse(**data)

    async def download_artifact(self, url: str) -> bytes:
        """Lädt eine Ergebnisdatei (Präsentation) von Manus herunter."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.content

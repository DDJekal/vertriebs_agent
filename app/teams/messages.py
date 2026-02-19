"""Teams Messaging-Endpoint – empfängt Nachrichten von Bot Framework."""

from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity

from app.config import settings
from app.database import SessionLocal
from app.teams.bot import SalesBot

adapter_settings = BotFrameworkAdapterSettings(
    app_id=settings.microsoft_app_id,
    app_password=settings.microsoft_app_password,
    channel_auth_tenant=settings.microsoft_tenant_id or None,
)
adapter = BotFrameworkAdapter(adapter_settings)
bot = SalesBot(db_session_factory=SessionLocal)


async def on_error(context: TurnContext, error: Exception):
    """Globaler Error Handler für den Bot."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error("Bot Error: %s", error, exc_info=True)
    await context.send_activity("Ein Fehler ist aufgetreten. Bitte versuche es erneut.")


adapter.on_turn_error = on_error


async def handle_teams_message(request):
    """FastAPI-kompatibler Handler für eingehende Teams-Nachrichten.

    Wird von POST /api/teams/messages aufgerufen.
    """
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return response
    return {"status": "ok"}

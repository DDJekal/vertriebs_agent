"""Slack Bolt App – Konfiguration und Event-Registrierung."""

import logging
import re
from slack_bolt.async_app import AsyncApp

from app.config import settings
from app.database import SessionLocal
from app.slack.handler import handle_slack_message

logger = logging.getLogger(__name__)

slack_app = AsyncApp(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
)

_MENTION_RE = re.compile(r"<@[A-Z0-9]+>")


@slack_app.event("message")
async def message_handler(event, say):
    """Handler für eingehende Slack-Nachrichten (DMs und Channels)."""
    if event.get("subtype") is not None:
        return

    db = SessionLocal()
    try:
        await handle_slack_message(event, say, db)
    except Exception as e:
        logger.error("Fehler in Slack Message Handler: %s", e, exc_info=True)
        await say("Ein Fehler ist aufgetreten. Bitte versuche es erneut.")
    finally:
        db.close()


@slack_app.event("app_mention")
async def mention_handler(event, say):
    """Handler für Bot-Mentions (@BotName)."""
    text = event.get("text", "")
    text = _MENTION_RE.sub("", text).strip()
    event["text"] = text
    await message_handler(event, say)

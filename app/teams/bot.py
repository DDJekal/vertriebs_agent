"""Teams Bot – ActivityHandler für eingehende Nachrichten."""

import json
import logging

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

from app.input_processor import (
    build_manus_prompt,
    classify_input,
    extract_fields,
    validate_fields,
)
from app.manus.client import ManusClient
from app.models.task import AnalysisTask, TaskStatus

logger = logging.getLogger(__name__)


class SalesBot(ActivityHandler):
    """Teams Bot der Wettbewerbsanalyse-Briefings entgegennimmt."""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    async def on_message_activity(self, turn_context: TurnContext):
        """Verarbeitet eingehende Nachrichten in Teams."""
        text = turn_context.activity.text or ""

        text = self._strip_mention(text, turn_context)
        text = text.strip()

        if not text:
            await turn_context.send_activity("Bitte sende ein Briefing mit Unternehmen, Position und Standort.")
            return

        if text.lower() in ("hilfe", "help", "?"):
            await turn_context.send_activity(self._help_text())
            return

        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name or "Unbekannt"
        conversation_id = turn_context.activity.conversation.id

        conv_ref = TurnContext.get_conversation_reference(turn_context.activity)
        conv_ref_json = json.dumps(conv_ref.serialize(), ensure_ascii=False)

        modus = classify_input(text)
        extraction = await extract_fields(text, modus)
        validation = validate_fields(extraction)

        if not validation.is_valid:
            await turn_context.send_activity(validation.reply_message)
            return

        manus_prompt = build_manus_prompt(extraction)

        db = self.db_session_factory()
        try:
            task = AnalysisTask(
                unternehmen=extraction.unternehmen,
                standort=extraction.standort,
                position=extraction.position,
                zusatzkontext=extraction.zusatzkontext,
                manus_prompt=manus_prompt,
                input_modus=modus.value,
                teams_user_id=user_id,
                teams_user_name=user_name,
                teams_conversation_id=conversation_id,
                teams_activity_id=turn_context.activity.id,
                conversation_reference=conv_ref_json,
                status=TaskStatus.PROCESSING,
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            await turn_context.send_activity(validation.reply_message)

            try:
                manus_client = ManusClient()
                manus_response = await manus_client.create_task(manus_prompt)
                task.manus_task_id = manus_response.task_id
                db.commit()
                logger.info(
                    "Manus task %s erstellt für %s (DB task %s)",
                    manus_response.task_id,
                    extraction.unternehmen,
                    task.id,
                )
            except Exception as e:
                logger.error("Manus API Fehler: %s", e)
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                db.commit()
                await turn_context.send_activity(
                    f"Fehler bei der Manus-API: {e}\nBitte versuche es erneut."
                )
        finally:
            db.close()

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """Begrüßung wenn der Bot einer Gruppe hinzugefügt wird."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hallo! Ich bin der SalesBot.\n\n"
                    "Schicke mir ein Briefing und ich erstelle eine "
                    "Wettbewerbsanalyse-Präsentation.\n\n"
                    'Schreibe "hilfe" für Details.'
                )

    def _strip_mention(self, text: str, turn_context: TurnContext) -> str:
        """Entfernt den @BotName-Tag aus der Nachricht."""
        if turn_context.activity.entities:
            for entity in turn_context.activity.entities:
                if entity.type == "mention":
                    mention_text = entity.additional_properties.get("text", "")
                    if mention_text:
                        text = text.replace(mention_text, "")
        return text

    def _help_text(self) -> str:
        return (
            "**SalesBot – Wettbewerbsanalyse**\n\n"
            "Schicke mir ein Briefing in einem der folgenden Formate:\n\n"
            "**Kurzformat:**\n"
            "```\nDRK Kreisverband Lausitz e.V.\nHEP\nLausitz\n```\n\n"
            "**Ausführlich (mit Pain Points):**\n"
            "```\nDRK Kreisverband Lausitz e.V.\n2-3 HEPs, Lausitz\n"
            "Rentenwelle, Agenturversagen, Ghosting...\n```\n\n"
            "**Strukturiert:**\n"
            "```\n**Unternehmen:** Name\n**Standort:** Stadt\n"
            "**Position:** Berufsbezeichnung\n```\n\n"
            "Ich extrahiere die Daten, erstelle einen Manus-Auftrag "
            "und schicke dir die fertige Präsentation."
        )

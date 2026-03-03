"""Baut den normalisierten Manus-Prompt aus den extrahierten Feldern."""

from app.input_processor.extractor import ExtractionResult

# Skill-Anweisung steht in den Project Instructions (System-Prompt).
# Der Bot sendet nur die strukturierte Anfrage – kein Slash-Command.
SKILL_PREAMBLE = "Erstelle eine Wettbewerbsanalyse für:\n\n"

SKILL_POSTAMBLE = (
    "\n\n---\n"
    "**Zusätzliche Regeln:**\n"
    "- Arbeite den GESAMTEN Workflow autonom ab – stelle KEINE Zwischenfragen "
    "und warte NICHT auf Bestätigung. Es gibt keinen interaktiven User.\n"
    "- Die HTML-Basis kommt aus dem Python-Skript (`--html-dir`). "
    "Lade die generierten HTMLs in Manus Slides, dann visuell prüfen "
    "und bei Abweichungen per `slide_edit` nachkorrigieren.\n"
    "- Gleiche das Ergebnis mit den Referenz-PDFs im Projektkontext ab "
    "und ergänze fehlende Elemente per `slide_edit`.\n"
    "- Kein Inhalt darf den Footer überlappen (untere 44px sind reserviert).\n"
    "- Exportiere als PDF und hänge die Datei direkt an. Keine Links, keine Viewer-URLs.\n"
)


def build_manus_prompt(extraction: ExtractionResult) -> str:
    """Generiert den Prompt im Manus-Eingabeformat inkl. Skill-Anweisung."""

    prompt = (
        f"{SKILL_PREAMBLE}"
        f"**Unternehmen:** {extraction.unternehmen}\n"
        f"**Standort:** {extraction.standort}\n"
        f"**Position:** {extraction.position}"
    )

    if extraction.zusatzkontext:
        prompt += (
            "\n\n**Zusätzlicher Kontext aus dem Erstgespräch:**\n"
            f"{extraction.zusatzkontext}"
        )

    prompt += SKILL_POSTAMBLE

    return prompt

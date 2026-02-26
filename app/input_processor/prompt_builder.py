"""Baut den normalisierten Manus-Prompt aus den extrahierten Feldern."""

from app.input_processor.extractor import ExtractionResult

SKILL_INSTRUCTION = (
    "⛔ PFLICHT-ANWEISUNG (vor allem anderen ausführen):\n"
    "Lies als ALLERERSTEN Schritt die Datei "
    "`/home/ubuntu/skills/wettbewerbsanalyse-generator-v2/SKILL.md` "
    "und folge dem dort definierten Workflow EXAKT. "
    "Erstelle die HTML-Folien AUSSCHLIESSLICH über das Python-Skript – "
    "NIEMALS manuell per slide_edit HTML schreiben.\n\n"
)


def build_manus_prompt(extraction: ExtractionResult) -> str:
    """Generiert den Prompt im Manus-Eingabeformat inkl. Skill-Anweisung."""

    prompt = (
        f"{SKILL_INSTRUCTION}"
        "Erstelle eine Wettbewerbsanalyse für:\n\n"
        f"**Unternehmen:** {extraction.unternehmen}\n"
        f"**Standort:** {extraction.standort}\n"
        f"**Position:** {extraction.position}"
    )

    if extraction.zusatzkontext:
        prompt += (
            "\n\n**Zusätzlicher Kontext aus dem Erstgespräch:**\n"
            f"{extraction.zusatzkontext}"
        )

    return prompt

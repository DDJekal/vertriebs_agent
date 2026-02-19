"""Baut den normalisierten Manus-Prompt aus den extrahierten Feldern."""

from app.input_processor.extractor import ExtractionResult


def build_manus_prompt(extraction: ExtractionResult) -> str:
    """Generiert den Prompt im Manus-Eingabeformat.

    Basiert auf dem definierten Manus-Input-Format:
        Erstelle eine Wettbewerbsanalyse für:
        **Unternehmen:** [Name + Rechtsform]
        **Standort:** [Stadt, Bundesland]
        **Position:** [Berufsbezeichnung]
    """

    prompt = (
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

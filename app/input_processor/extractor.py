"""Extrahiert die 3 Manus-Pflichtfelder aus dem User-Input.

Verwendet einen zweistufigen Ansatz:
1. Regelbasiert (schnell, kostenlos) für strukturierte und einfache Inputs
2. LLM-basiert (OpenAI) als Fallback für komplexe Freitext-Inputs
"""

import re
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from app.config import settings
from app.input_processor.classifier import InputModus
from app.input_processor.taxonomy import resolve_position

EXTRACTION_SYSTEM_PROMPT = """\
Du bist ein Extraktions-Assistent für ein Recruiting-Unternehmen.
Deine Aufgabe: Extrahiere aus dem folgenden Text exakt drei Felder:

1. **unternehmen**: Vollständiger Name inkl. Rechtsform (z.B. "DRK Kreisverband Lausitz e.V.")
2. **standort**: Stadt/Region + Bundesland (z.B. "Lausitz, Brandenburg")
3. **position**: Berufsbezeichnung der gesuchten Fachkraft (z.B. "Heilerziehungspfleger")

Zusätzlich extrahiere:
4. **zusatzkontext**: Alle weiteren relevanten Informationen (Pain Points, Mitarbeiterzahlen, etc.)
   Falls keine vorhanden, setze auf null.

Antworte ausschließlich im folgenden JSON-Format, ohne Markdown-Codeblöcke:
{"unternehmen": "...", "standort": "...", "position": "...", "zusatzkontext": "..."}

Wenn ein Feld nicht erkennbar ist, setze es auf null.
Verwende für die Position immer die vollständige Berufsbezeichnung (nicht die Abkürzung)."""


@dataclass
class ExtractionResult:
    unternehmen: str | None = None
    standort: str | None = None
    position: str | None = None
    zusatzkontext: str | None = None
    raw_input: str = ""
    input_modus: InputModus = InputModus.MINIMAL
    used_llm: bool = False
    errors: list[str] = field(default_factory=list)


def _extract_structured(text: str) -> ExtractionResult:
    """Extrahiert Felder aus einem klar strukturierten Input mit **Feld:**-Syntax."""
    result = ExtractionResult(raw_input=text, input_modus=InputModus.STRUCTURED)

    patterns = {
        "unternehmen": r"\*\*\s*unternehmen\s*:\*\*\s*(.+)",
        "standort": r"\*\*\s*standort\s*:\*\*\s*(.+)",
        "position": r"\*\*\s*position\s*:\*\*\s*(.+)",
    }

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            setattr(result, field_name, match.group(1).strip())

    if result.position:
        resolved = resolve_position(result.position)
        if resolved:
            result.position = resolved

    return result


def _extract_minimal(text: str) -> ExtractionResult:
    """Extrahiert Felder aus einem Minimal Input (3-4 Zeilen)."""
    result = ExtractionResult(raw_input=text, input_modus=InputModus.MINIMAL)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if len(lines) >= 1:
        result.unternehmen = lines[0]
    if len(lines) >= 2:
        raw_position = lines[1]
        resolved = resolve_position(raw_position)
        result.position = resolved if resolved else raw_position
    if len(lines) >= 3:
        result.standort = lines[2]

    return result


async def _extract_with_llm(text: str, modus: InputModus) -> ExtractionResult:
    """Verwendet OpenAI für die Extraktion aus komplexem Freitext."""
    import json

    result = ExtractionResult(
        raw_input=text, input_modus=modus, used_llm=True
    )

    if not settings.openai_api_key:
        result.errors.append("OpenAI API Key nicht konfiguriert – LLM-Extraktion nicht möglich")
        return result

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.0,
            max_tokens=500,
        )

        raw_json = response.choices[0].message.content.strip()
        raw_json = raw_json.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw_json)

        result.unternehmen = data.get("unternehmen")
        result.standort = data.get("standort")
        result.position = data.get("position")
        result.zusatzkontext = data.get("zusatzkontext")

        if result.position:
            resolved = resolve_position(result.position)
            if resolved:
                result.position = resolved

    except json.JSONDecodeError as e:
        result.errors.append(f"LLM-Antwort konnte nicht geparst werden: {e}")
    except Exception as e:
        result.errors.append(f"LLM-Extraktion fehlgeschlagen: {e}")

    return result


async def extract_fields(text: str, modus: InputModus) -> ExtractionResult:
    """Hauptfunktion: Extrahiert Felder basierend auf dem Input-Modus."""

    if modus == InputModus.STRUCTURED:
        return _extract_structured(text)

    if modus == InputModus.MINIMAL:
        result = _extract_minimal(text)
        if result.unternehmen and result.standort and result.position:
            return result
        return await _extract_with_llm(text, modus)

    # Rich Input → immer LLM
    return await _extract_with_llm(text, modus)

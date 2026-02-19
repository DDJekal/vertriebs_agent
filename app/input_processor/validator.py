"""Validiert extrahierte Felder und erzeugt Rückfrage-Nachrichten bei fehlenden/mehrdeutigen Daten."""

from dataclasses import dataclass, field

from app.input_processor.extractor import ExtractionResult
from app.input_processor.taxonomy import (
    AMBIGUOUS_TERMS,
    DISAMBIGUATION_OPTIONS,
    resolve_position,
)


@dataclass
class ValidationResult:
    is_valid: bool = False
    missing_fields: list[str] = field(default_factory=list)
    ambiguous_fields: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    reply_message: str | None = None
    extraction: ExtractionResult | None = None


def validate_fields(extraction: ExtractionResult) -> ValidationResult:
    """Prüft ob alle Pflichtfelder vorhanden und eindeutig sind."""

    result = ValidationResult(extraction=extraction)

    if not extraction.unternehmen:
        result.missing_fields.append("unternehmen")
    if not extraction.standort:
        result.missing_fields.append("standort")

    if not extraction.position:
        result.missing_fields.append("position")
    elif extraction.position.strip().lower() in AMBIGUOUS_TERMS:
        result.ambiguous_fields["position"] = DISAMBIGUATION_OPTIONS
        extraction.position = None

    if result.missing_fields or result.ambiguous_fields:
        result.is_valid = False
        result.reply_message = _build_reply(result, extraction)
    else:
        result.is_valid = True
        result.reply_message = _build_confirmation(extraction)

    return result


def apply_user_choice(
    extraction: ExtractionResult,
    field_name: str,
    choice_key: str,
) -> ExtractionResult:
    """Wendet die Auswahl des Users auf ein mehrdeutiges Feld an."""

    if field_name == "position":
        for option in DISAMBIGUATION_OPTIONS:
            if option["key"] == choice_key:
                extraction.position = option["value"]
                break

    return extraction


def _build_reply(
    validation: ValidationResult, extraction: ExtractionResult
) -> str:
    parts: list[str] = []

    if extraction.unternehmen:
        parts.append(f"Erkannt: {extraction.unternehmen}")

    if "position" in validation.ambiguous_fields:
        raw = extraction.raw_input.strip().split("\n")
        ambig_term = next(
            (line for line in raw if line.strip().lower() in AMBIGUOUS_TERMS),
            "Pfleger",
        )
        parts.append(f'\n"{ambig_term}" ist mehrdeutig. Meinst du:')
        for opt in DISAMBIGUATION_OPTIONS:
            parts.append(f"  {opt['key']}. {opt['label']}")

    if validation.missing_fields:
        field_labels = {
            "unternehmen": "Unternehmensname",
            "standort": "Standort (Stadt/Region)",
            "position": "Position / Berufsbezeichnung (z.B. HEP, PFK, Erzieher)",
        }
        for f in validation.missing_fields:
            if f not in validation.ambiguous_fields:
                parts.append(f"\nWelche(r) {field_labels.get(f, f)}?")

    return "\n".join(parts)


def _build_confirmation(extraction: ExtractionResult) -> str:
    lines = [
        f"Unternehmen: {extraction.unternehmen}",
        f"Position:    {extraction.position}",
        f"Standort:    {extraction.standort}",
    ]

    if extraction.zusatzkontext:
        ctx_preview = extraction.zusatzkontext[:120]
        if len(extraction.zusatzkontext) > 120:
            ctx_preview += "..."
        lines.append(f"\nZusatzkontext: {ctx_preview}")

    lines.append("\nWettbewerbsanalyse wird erstellt...")

    return "\n".join(lines)

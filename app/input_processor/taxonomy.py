"""Berufsgruppen-Taxonomie für die Normalisierung von Zielgruppen/Positionen."""

POSITION_MAP: dict[str, str] = {
    # Heilerziehungspfleger
    "hep": "Heilerziehungspfleger",
    "heilerziehungspfleger": "Heilerziehungspfleger",
    "heilerziehungspflegerin": "Heilerziehungspfleger",
    "heilerziehungspfleger/in": "Heilerziehungspfleger",
    # Pflegefachkraft
    "pfk": "Pflegefachkraft",
    "pflegefachkraft": "Pflegefachkraft",
    "pflegefachfrau": "Pflegefachkraft",
    "pflegefachmann": "Pflegefachkraft",
    "exam. pflegekraft": "Pflegefachkraft",
    "examinierte pflegekraft": "Pflegefachkraft",
    "krankenschwester": "Pflegefachkraft",
    "krankenpfleger": "Pflegefachkraft",
    "gesundheits- und krankenpfleger": "Pflegefachkraft",
    # Erzieher
    "erzieher": "Erzieher",
    "erzieherin": "Erzieher",
    "erzieher/in": "Erzieher",
    # Altenpfleger
    "ap": "Altenpfleger",
    "altenpfleger": "Altenpfleger",
    "altenpflegerin": "Altenpfleger",
    "altenpfleger/in": "Altenpfleger",
    # OTA
    "ota": "OTA",
    "op-pflege": "OTA",
    "op-pflegekraft": "OTA",
    "operationstechnischer assistent": "OTA",
    "operationstechnische assistentin": "OTA",
    # Sozialarbeiter
    "sozialarbeiter": "Sozialarbeiter",
    "sozialarbeiterin": "Sozialarbeiter",
    "sozialpädagoge": "Sozialarbeiter",
    "sozialpädagogin": "Sozialarbeiter",
    "sozialarbeiter/in": "Sozialarbeiter",
}

AMBIGUOUS_TERMS: set[str] = {
    "pfleger",
    "pflegerin",
    "pflege",
    "pflegekraft",
    "fachkraft",
}

DISAMBIGUATION_OPTIONS: list[dict[str, str]] = [
    {"key": "1", "label": "Pflegefachkraft (PFK)", "value": "Pflegefachkraft"},
    {"key": "2", "label": "Heilerziehungspfleger (HEP)", "value": "Heilerziehungspfleger"},
    {"key": "3", "label": "Altenpfleger/in", "value": "Altenpfleger"},
    {"key": "4", "label": "Pflegehelfer / Pflegeassistent", "value": "Pflegehelfer"},
]


def resolve_position(raw: str) -> str | None:
    """Versucht eine Position aus der Taxonomie aufzulösen.

    Returns:
        Normalisierte Position oder None bei mehrdeutigen/unbekannten Eingaben.
    """
    normalized = raw.strip().lower()
    if normalized in AMBIGUOUS_TERMS:
        return None
    return POSITION_MAP.get(normalized)

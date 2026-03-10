"""Erkennt ob ein Input Rich (Gesprächsnotizen), Minimal (3-4 Felder) oder Talent-Report ist."""

import enum
import re


class InputModus(str, enum.Enum):
    RICH = "rich"
    MINIMAL = "minimal"
    STRUCTURED = "structured"
    TALENT_REPORT = "talent_report"


_TALENT_REPORT_PATTERN = re.compile(
    r"^\s*talent[-\s]?report\b",
    re.IGNORECASE,
)


_RICH_INDICATORS = [
    r"rentenwelle",
    r"ghosting",
    r"pain\s*point",
    r"krankenstand",
    r"fachkräftemangel",
    r"agentur",
    r"arbeitnehmerüberlassung",
    r"leiharbeit",
    r"schwäche",
    r"stärke",
    r"risik",
    r"einrichtung",
    r"mitarbeiter",
    r"bewerber",
    r"rekrutierung",
    r"schichtmodell",
    r"wechsel",
    r"müssen wachsen",
    r"in rente",
    r"eingestellt",
    r"unqualifiziert",
]

_STRUCTURED_PATTERN = re.compile(
    r"\*\*\s*unternehmen\s*:\*\*.*\*\*\s*standort\s*:\*\*.*\*\*\s*position\s*:\*\*",
    re.IGNORECASE | re.DOTALL,
)


def classify_input(text: str) -> InputModus:
    """Klassifiziert den Input-Modus anhand von Heuristiken."""

    if _TALENT_REPORT_PATTERN.search(text):
        return InputModus.TALENT_REPORT

    if _STRUCTURED_PATTERN.search(text):
        return InputModus.STRUCTURED

    text_lower = text.lower()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    rich_score = sum(
        1 for pattern in _RICH_INDICATORS
        if re.search(pattern, text_lower)
    )

    if rich_score >= 3:
        return InputModus.RICH

    if len(lines) <= 5 and rich_score == 0:
        return InputModus.MINIMAL

    if len(lines) > 8:
        return InputModus.RICH

    return InputModus.MINIMAL

"""Baut den normalisierten Manus-Prompt aus den extrahierten Feldern."""

from app.input_processor.extractor import ExtractionResult

# Slash-Command aktiviert den Skill direkt in Manus (zuverlaessiger als nur Systemprompt).
SKILL_PREAMBLE = "/wettbewerbsanalyse-generator-v2\n\nErstelle eine Wettbewerbsanalyse für:\n\n"

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
    "\n"
    "**BILDER – PFLICHT (nicht überspringen!):**\n"
    "- **Folie 1 (Titelfolie):** Recherchiere ein hochauflösendes Stadtbild/Panorama "
    "des Standorts (mind. 1280x720 px). Wikimedia Commons: `[Stadtname] panorama` oder "
    "`[Stadtname] cityscape`. Trage die URL in `background_image_url` ein. "
    "Stadtbilder sind IMMER verfügbar – dieses Feld darf NICHT leer bleiben.\n"
    "- **Folie 2 (Wettbewerber):** Recherchiere pro Wettbewerber ein Foto des "
    "Unternehmensgebäudes (mind. 800x400 px). Trage die URL in `building_image_url` "
    "pro Wettbewerber ein. Fallback: Logo über `logo_url` oder Clearbit (`domain`).\n"
    "- **Bildqualität:** Keine kleinen Thumbnails (250px, 500px). Bei Wikimedia immer "
    "Original oder große Vorschau (1280px+) verwenden. Verpixelte Bilder zerstören "
    "den professionellen Eindruck.\n"
    "\n"
    "**REGIONALE STATISTIKEN (Folie 3) – PFLICHT:**\n"
    "- Die 4 `regional_stats` beziehen sich auf **verfügbare Personen mit dem "
    "Stellentitel** im 40-km-Umkreis (Fachkräfte-Pool), NICHT auf offene Stellen. "
    "Beispiele: Anzahl Fachkräfte mit dem Stellentitel in der Region, davon aktiv "
    "stellensuchend/wechselwillig, Arbeitgeber in der Branche, Trend.\n"
    "\n"
    "**CHANCEN (Folie 6) – PFLICHT:**\n"
    "- Wähle 3 passende Dienstleistungen aus dem Pool in der SKILL.md "
    "(z.B. Social Recruiting, Employer Branding, Pflegepersonal finden). "
    "Bullets müssen konkret auf die Schwächen der Wettbewerber eingehen.\n"
    "\n"
    "**LOGO – PFLICHT:**\n"
    "- Das Logo für den Footer liegt im Skill-Ordner unter `templates/` "
    "(SVG oder PNG). Das Python-Skript lädt es automatisch.\n"
    "- Falls im **Projektordner** eine `logo.png` oder `logo.svg` liegt, "
    "wird diese stattdessen verwendet. Nutze dann `--project-dir .` beim "
    "Skript-Aufruf, damit das Projektlogo korrekt geladen wird.\n"
    "- Prüfe nach dem Generieren, dass das Logo im Footer jeder Folie "
    "sichtbar ist. Fehlt es, lade es manuell als base64 nach.\n"
    "\n"
    "**ALLE 7 FOLIEN – PFLICHT:**\n"
    "- Lade JEDE der 7 HTML-Folien (slide_01.html bis slide_07.html) "
    "nacheinander per `slide_edit`. KEINE Folie ueberspringen.\n"
    "- ERST wenn alle 7 geladen und geprueft sind, als PDF exportieren.\n"
    "- Das Radar (Folie 3), Balkendiagramm (Folie 4) und alle "
    "Kartenstrukturen kommen fertig aus dem Skript – NICHT per "
    "`slide_edit` umbauen oder ersetzen. Das Radar ist ein einfacher "
    "SVG-Kreis (40km/20km-Ringe), KEIN Dimensionsradar, KEIN Spinnendiagramm.\n"
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

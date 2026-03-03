---
name: wettbewerbsanalyse-generator-v2
description: "Erstellt vollautomatisierte Wettbewerbsanalysen als 7-Folien-Präsentation im HiOffice-Design (v2.4). CI: #001666 Blau, #EF5800 Orange. Hybrid-Workflow: Python-Skript generiert HTML-Basis, slide_edit für Feinschliff anhand Referenz-PDFs. Output ist eine PDF-Datei als direkter Anhang."
---

# Wettbewerbsanalyse Generator v2.4

## Input

```
Unternehmen: [Name + Rechtsform]
Standort:    [Stadt, Bundesland]
Position:    [Berufsbezeichnung]
```

---

## Vorlage & CI

- **Python-Skript:** `/home/ubuntu/skills/wettbewerbsanalyse-generator-v2/scripts/generate_presentation.py`
- **CI-Logo (SVG):** `/home/ubuntu/skills/wettbewerbsanalyse-generator-v2/templates/Hioffice_logo_white.svg`

| Parameter | Wert |
|---|---|
| Hintergrund | `#001666` |
| Akzent Orange | `#EF5800` |
| Akzent Blau (Chancen) | `#4A90D9` |
| SWOT Stärken | `#27AE60` |
| SWOT Schwächen | `#E74C3C` |
| SWOT Risiken | `#EF5800` |
| Persona 1 | `#EF5800` |
| Persona 2 | `#4A90D9` |
| Persona 3 | `#27AE60` |
| Schrift | Inter (Google Fonts) |
| Footer | `@HiOffice Group 2026` + SVG-Logo |
| Format | 1280×720px (16:9) |

---

## Workflow (verbindlich, in dieser Reihenfolge)

### Schritt 1 – Marktrecherche & JSON erstellen

Recherchiere alle Daten und speichere sie als `/home/ubuntu/research_data.json`.

**Pflicht-Recherchen:**
1. Offizielle Website des Zielunternehmens → Mitarbeiterzahl, Benefits, Tarifvertrag
2. Stellenportale (Indeed, Stepstone, Bundesagentur Entgeltatlas) → Gehalt, offene Stellen
3. Für jeden Wettbewerber: Gebäudefoto-URL (Google Maps, offizielle Website, Wikimedia)
4. Hintergrundbild-URL für Titelfolie (Gebäude des Zielunternehmens)

Das JSON muss exakt folgendem Schema entsprechen:

```json
{
  "company_name": "Städtisches Klinikum Braunschweig gGmbH",
  "position": "Pflegefachkraft (m/w/d)",
  "location": "Braunschweig",
  "location_short": "BS",
  "background_image_url": "https://upload.wikimedia.org/...",
  "competitors": [
    {
      "name": "Herzogin Elisabeth Hospital",
      "image_url": "https://upload.wikimedia.org/...",
      "type": "Kirchlich (Stiftung)",
      "distance": "3 km",
      "employees": "ca. 950",
      "salary": "~3.450 € (AVR)",
      "strength": "Kirchliche Werte & familiäre Atmosphäre",
      "weakness": "AVR-Tarif liegt unter TVöD-P"
    }
  ],
  "regional_stats": [
    {"value": "≈ 12.500", "label": "Pflegefachkräfte im 30km Radius"},
    {"value": "14", "label": "Krankenhäuser im 30km Radius"},
    {"value": "450+", "label": "Offene Pflegestellen in der Region"},
    {"value": "+18%", "label": "Anstieg offener Stellen seit 2022"}
  ],
  "regional_insight": "Vollständiger Insight-Satz mit regionalem Kontext.",
  "salaries": [
    {"name": "Zielunternehmen", "salary": "3.600 €", "bar_color": "#EF5800"},
    {"name": "Wettbewerber 1", "salary": "3.550 €", "bar_color": "#001666"},
    {"name": "Wettbewerber 2", "salary": "3.450 €", "bar_color": "#001666"},
    {"name": "Wettbewerber 3", "salary": "3.400 €", "bar_color": "#001666"},
    {"name": "⌀ Bundesland (Pflege)", "salary": "3.320 €", "bar_color": "#aaa", "is_average": true}
  ],
  "swot": [
    {
      "title": "STÄRKEN", "color": "#27AE60", "icon": "✅",
      "points": [
        {"title": "Titel max. 35 Zeichen", "text": "Keyword – Erklärung max. 55 Zeichen"}
      ]
    },
    {"title": "SCHWÄCHEN", "color": "#E74C3C", "icon": "⚠", "points": [{"title": "...", "text": "..."}]},
    {"title": "RISIKEN", "color": "#EF5800", "icon": "⚡", "points": [{"title": "...", "text": "..."}]}
  ],
  "opportunities": [
    {
      "title": "DIREKTANSPRACHE", "color": "#4A90D9", "icon": "🎯",
      "bullets": ["Keyword – Erklärungstext (max. 65 Zeichen)"]
    },
    {"title": "AUSBILDUNGS-EXIT", "color": "#27AE60", "icon": "🎓", "bullets": ["..."]},
    {"title": "EMPLOYER BRANDING", "color": "#EF5800", "icon": "⭐", "bullets": ["..."]}
  ],
  "personas": [
    {
      "name": "Thomas, 34", "archetype": "Erfahrener Pflegefachmann · 8 Jahre",
      "color": "#EF5800",
      "pain_points": ["Keyword – Erklärung (max. 55 Zeichen)"],
      "values": ["Keyword – Erklärung (max. 55 Zeichen)"]
    }
  ]
}
```

**Recherche-Regeln:**
- Genau 3 Wettbewerber im 30–50 km Radius, keine Tochtergesellschaften des Zielunternehmens
- Pro Wettbewerber: stärkstes Argument + Schwäche (PFLICHT)
- Genau 4 `regional_stats` (2 links, 2 rechts auf Folie 3)
- Genau 5 `salaries` (Zielunternehmen + 3 Wettbewerber + Landes-Ø mit `"is_average": true`)
- Genau 3 SWOT-Kategorien mit je 4 Punkten
- Genau 3 Chancen mit je 4 Bullets
- Genau 3 Personas mit je 3 Schmerzpunkten + 3 Werten
- **Bilder (PFLICHT):** Reales Gebäudefoto-URL für Titelfolie + jeden Wettbewerber suchen.
  Priorität: Wikimedia Commons → offizielle Website → Google Maps Street View Screenshot-URL.
  Bei keinem Bild: leerer String `""` (Skript generiert automatisch Platzhalter mit Initialen).

---

### Schritt 2 – HTML-Folien generieren (PFLICHT – kein manuelles HTML von Grund auf!)

```bash
python3 /home/ubuntu/skills/wettbewerbsanalyse-generator-v2/scripts/generate_presentation.py \
  /home/ubuntu/research_data.json \
  --html-dir /home/ubuntu/slides/
```

Das Skript:
1. Lädt alle Bilder automatisch herunter und bettet sie als base64 ein
2. Generiert 7 HTML-Dateien (1280×720px, 16:9) in `/home/ubuntu/slides/`

**WICHTIG:** HTML-Grundgerüst IMMER über das Skript erzeugen, niemals komplett manuell schreiben.

---

### Schritt 3 – Folien in Manus Slides laden

```
slide_initialize  →  7 Folien, Format 1280×720
```

Dann für jede Folie 1–7:
1. HTML-Datei lesen: `/home/ubuntu/slides/slide_01.html` bis `slide_07.html`
2. Den `<body>`-Inhalt (alles zwischen `<body>` und `</body>`) per `slide_edit` als Content setzen

---

### Schritt 4 – Visueller Abgleich & Nachkorrektur mit `slide_edit`

1. Jede Folie visuell prüfen (Screenshot / Preview)
2. Mit den **Referenz-PDFs im Projektkontext** abgleichen
3. Per `slide_edit` korrigieren:
   - Fehlende Elemente ergänzen
   - Layout-Abweichungen beheben
   - Textüberlauf oder abgeschnittene Inhalte fixen
   - **Kein Inhalt darf den Footer überlappen** (untere 44px sind reserviert)

**Erlaubt bei `slide_edit`:** Positionierung, Schriftgrößen, Abstände, fehlende Elemente hinzufügen.
**Verboten:** Komplett neues HTML von Grund auf schreiben (Basis kommt IMMER aus dem Skript).

---

### Schritt 5 – Qualitätsprüfung & PDF-Export

**Checkliste (vor Export prüfen):**
- □ 7 Folien vorhanden
- □ Folie 1: Unternehmensname + Position lesbar, Hintergrundbild oder Gradient
- □ Folie 2: 3 Karten mit Bild/Platzhalter, Stärke-Box grün, Schwäche-Box rot
- □ Folie 3: Radar zentriert, 4 Statistik-Karten, Insight-Box
- □ Folie 4: 5 Gehaltszeilen links, Balkendiagramm rechts
- □ Folie 5: 3 SWOT-Kacheln (grün/rot/orange), je 4 Items
- □ Folie 6: 3 Chancen-Kacheln, je 4 Bullets mit Bold-Keywords
- □ Folie 7: 3 Persona-Karten, Schmerzpunkte rot, Werte grün
- □ ALLE: Footer `@HiOffice Group 2026` + Logo, Hintergrund `#001666`
- □ KEIN Inhalt überlappt den Footer (untere 44px)

Dann als **PDF exportieren** und als **direkten Anhang** senden

---

## Output (verbindlich)

Kurze Zusammenfassung der wichtigsten Erkenntnisse (3–5 Sätze) im Text, dann **PDF-Datei als direkter Anhang** – keine Links, keine Viewer-URLs.

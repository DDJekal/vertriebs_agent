---
name: wettbewerbsanalyse-talent-report
description: "Erstellt vollautomatisierte Wettbewerbsanalysen als 7-Folien-Praesentation im Talent-Report-Design. CI: #e0edc8 Limonengruen, #1a2e0d Dunkelgruen. Hybrid-Workflow: Python-Skript generiert HTML-Basis, slide_edit fuer Feinschliff anhand Referenz-PDFs. Output ist eine PDF-Datei als direkter Anhang."
---

# Wettbewerbsanalyse - Talent Report Layout

## Input

```
Unternehmen: [Name + Rechtsform]
Standort:    [Stadt, Bundesland]
Position:    [Berufsbezeichnung]
```

---

## Vorlage & Logo

- **Python-Skript:** `/home/ubuntu/skills/wettbewerbsanalyse-talent-report/scripts/generate_presentation.py`
- **Logo:** Das Skill enthaelt ein eingebautes Logo unter `templates/logo.png`. Optional: Eigene Datei **`logo.png`** oder **`logo.svg`** im **Projektordner** - wird dann statt des Skill-Logos verwendet. Aufruf mit `--project-dir .` wenn du im Projektroot arbeitest.

**CI-Vorgaben (exakt wie im Python-Skript - keine anderen Werte verwenden):**

| Verwendung | Variable im Skript | Hex / Wert |
|---|---|---|
| Folien-Hintergrund | `BG` | `#e0edc8` (Helles Limonengruen) |
| Footer, Titellinie, Akzente, Radar-Mitte | `DARK` / `ACCENT` | `#1a2e0d` (Dunkelgruen) |
| Text auf weissen Karten | `CARD_TEXT` | `#1a1a1a` |
| Footer-Text auf dunklem Streifen | - | `#e0edc8` |
| SWOT Staerken | `SWOT_STRENGTH` | `#27AE60` |
| SWOT Schwaechen | `SWOT_WEAKNESS` | `#E74C3C` |
| SWOT Risiken | `SWOT_RISK` | `#f9a825` |
| Chancen-Karten (Standard) | `CHANCE_DEFAULT` | `#81c784` |
| Schrift | - | Inter (Google Fonts) |
| Format | - | 1280x720px (16:9) |

Referenz-PDFs im Projekt dienen nur als Layout-Vorbild; die **Farbwerte** entnimm ausschliesslich dieser Tabelle bzw. dem Skript.

---

## Workflow (verbindlich, in dieser Reihenfolge)

### Schritt 1 - Marktrecherche & JSON erstellen

Recherchiere alle Daten und speichere sie als `/home/ubuntu/research_data.json`.

**Pflicht-Recherchen:**
1. Offizielle Website des Zielunternehmens - Mitarbeiterzahl, Benefits, Tarifvertrag
2. Stellenportale (Indeed, Stepstone, Bundesagentur Entgeltatlas) - Gehalt, offene Stellen
3. **Standortbild Folie 1 (PFLICHT, hohe Aufloesung):** Suche ein **Stadtbild/Panorama des Standorts** in **mind. 1280x720 px** (Wikimedia Commons: `[Stadtname] panorama` oder `[Stadtname] cityscape`, Original oder grosse Vorschau, keine kleinen Thumbnails). Feld: `background_image_url`. Stadtbilder sind immer verfuegbar - leerer String ist NICHT akzeptabel.
4. **Unternehmensgebaeude Folie 2 (PFLICHT, hohe Aufloesung):** Pro Wettbewerber ein Foto des **Unternehmensgebaeudes** in **mind. ca. 800x400 px** (Wikimedia Commons, offizielle Website, keine 250px-Thumbnails). Feld pro Wettbewerber: `building_image_url`. Fallback: Logo (`logo_url` / Clearbit).

Das JSON muss folgendem Schema entsprechen:

```json
{
  "company_name": "brayn.io GmbH",
  "position": "Softwareentwickler (m/w/d)",
  "location": "Berlin",
  "location_short": "BE",
  "background_image_url": "https://upload.wikimedia.org/.../Berlin_panorama.jpg",
  "competitors": [
    {
      "name": "Assesor GmbH",
      "logo_url": "https://logo.clearbit.com/assesor.de",
      "building_image_url": "https://upload.wikimedia.org/.../Assesor_Gebaeude.jpg",
      "domain": "assesor.de",
      "type": "IT-Beratung",
      "distance": "4 km",
      "employees": "ca. 80-120",
      "salary": "5.400 EUR",
      "strength": "360 Grad IT-Dienstleister, KI-Expertise",
      "weakness": "Wenig Fokus auf Nachhaltigkeit"
    }
  ],
  "regional_stats": [
    {"value": "38.000", "label": "IT-Fachkraefte im 40-km-Umkreis (verfuegbar/wechselwillig)"},
    {"value": "1.200+", "label": "IT-Arbeitgeber im 40-km-Radius"},
    {"value": "4.500", "label": "Davon aktiv stellensuchend (Softwareentwickler)"},
    {"value": "-5%", "label": "Rueckgang verfuegbarer Entwickler seit 2023"}
  ],
  "regional_insight": "Vollstaendiger Insight-Satz mit regionalem Kontext.",
  "salaries": [
    {"name": "Zielunternehmen", "salary": "5.429 EUR", "bar_color": "#1a2e0d"},
    {"name": "Wettbewerber 1", "salary": "5.400 EUR", "bar_color": "#1a2e0d"},
    {"name": "Wettbewerber 2", "salary": "5.200 EUR", "bar_color": "#1a2e0d"},
    {"name": "Wettbewerber 3", "salary": "5.100 EUR", "bar_color": "#1a2e0d"},
    {"name": "Durchschnitt Berlin Softwareentwickler", "salary": "5.429 EUR", "bar_color": "#aaa", "is_average": true}
  ],
  "swot": [
    {"title": "STAERKEN", "color": "#27AE60", "icon": "check", "points": [{"title": "...", "text": "..."}]},
    {"title": "SCHWAECHEN", "color": "#E74C3C", "icon": "warning", "points": [{"title": "...", "text": "..."}]},
    {"title": "RISIKEN", "color": "#f9a825", "icon": "risk", "points": [{"title": "...", "text": "..."}]}
  ],
  "opportunities": [
    {"title": "[DIENSTLEISTUNG AUS POOL]", "color": "#4A90D9", "bullets": ["...", "...", "...", "..."]},
    {"title": "[DIENSTLEISTUNG AUS POOL]", "color": "#27AE60", "bullets": ["...", "...", "...", "..."]},
    {"title": "[DIENSTLEISTUNG AUS POOL]", "color": "#81c784", "bullets": ["...", "...", "...", "..."]}
  ],
  "personas": [
    {"name": "Lena, 28", "archetype": "Junior Softwareentwicklerin - 2 Jahre", "color": "#1a2e0d", "pain_points": ["..."], "values": ["..."]}
  ]
}
```

**Recherche-Regeln:**
- Genau 3 Wettbewerber im 30-50 km Radius, keine Tochtergesellschaften des Zielunternehmens
- Pro Wettbewerber: staerkstes Argument + Schwaeche (PFLICHT), **sowie Logo** (`logo_url` und `domain`) und **Gebaeudebild** (`building_image_url`)
- Genau 4 `regional_stats` (2 links, 2 rechts auf Folie 3) - PFLICHT: Alle 4 Werte beziehen sich auf die **verfuegbaren Personen mit dem Stellentitel** (Fachkraefte-Pool) im 40-km-Umkreis, NICHT auf offene Stellen. Beispiele: Anzahl Fachkraefte mit dem Stellentitel in der Region, davon aktiv stellensuchend/wechselwillig, Anzahl Arbeitgeber in der Branche im Umkreis, Trend (Rueckgang/Zuwachs) verfuegbarer Fachkraefte.
- Genau 5 `salaries`, 3 SWOT (je 4 Punkte), 3 Chancen (je 4 Bullets), 3 Personas (je 3 Schmerzpunkte + 3 Werte)

**Bilder (PFLICHT):**
- **Folie 1 - Titelfolie:** `background_image_url`: **Stadtbild/Panorama des Standorts** (Wikimedia Commons: `[Stadtname] panorama` oder `[Stadtname] cityscape`). **PFLICHT - darf NICHT leer sein.** Stadtbilder sind immer verfuegbar.
- **Folie 2 - Wettbewerber-Karten:** Pro Wettbewerber `building_image_url`: Foto des **Unternehmensgebaeudes** (Wikimedia Commons, offizielle Website). Fallback im Skript: Logo. Prioritaet Logo, wenn kein Gebaeude:
  1. `logo_url` oder `https://logo.clearbit.com/[domain]`
  2. Logo von der offiziellen Website
  3. Leer - Skript zeigt Initialen-Platzhalter
  **PFLICHT:** `domain` immer befuellen (z.B. `"unternehmen.de"`), damit Clearbit-Fallback funktioniert.

**Bildqualitaet (PFLICHT - keine verpixelten Bilder):**
- **Folie 1 (Hintergrund, Vollbild 1280x720 px):** Mindestens **1280x720 px**, idealerweise groesser. Bei Wikimedia: **Original** oder grosse Vorschau, **keine** kleinen Thumbnail-URLs (250px-, 500px-).
- **Folie 2 (Wettbewerber-Karten, ca. 400x120 px sichtbar):** Pro Gebaeude-Foto mindestens **ca. 800x400 px**. Bei Wikimedia: 800px- oder 1000px- Vorschau, keine 200px-/250px-Thumbnails.
- **Allgemein:** Immer die groesste sinnvoll verfuegbare Version verlinken.

**Chancen (opportunities) - PFLICHT: Dienstleistungen dynamisch auswaehlen:**
Waehle die **3 zur Branche und Zielgruppe am besten passenden** Dienstleistungen aus diesem Pool:

| Dienstleistung | Wann verwenden |
|---|---|
| `SOCIAL RECRUITING AGENTUR` | immer einsetzbar - passt fuer alle Branchen |
| `EMPLOYER BRANDING AGENTUR` | immer einsetzbar - passt fuer alle Branchen |
| `PERFORMANCE RECRUITING AGENTUR` | immer einsetzbar - wenn Kosten/Effizienz ein Thema |
| `PERSONALMARKETING AGENTUR` | bei groesseren Unternehmen, wenn Markenpositionierung relevant |
| `EMPLOYER BRANDING VIDEO` | wenn Unternehmenskultur, Authentizitaet oder Mitarbeiterbindung ein Thema |
| `RECRUITING FILME` | wenn emotionales Storytelling oder Azubi-Recruiting relevant |
| `PFLEGEPERSONAL FINDEN` | nur Pflege, Gesundheit, Klinik, Seniorenheim |
| `MITARBEITER FINDEN IM HANDWERK` | nur Handwerk, Bau, SHK, Elektro, Industrie |

**Auswahlregel:** Branchenspezifische Dienstleistungen haben Vorrang wenn sie zur Zielgruppe passen. Ergaenze mit allgemeinen Dienstleistungen bis du 3 hast.

**Bullets-Regel:** Die Bullets jeder Karte muessen konkret auf die **Schwaechen des analysierten Wettbewerbers** und die **Beduerfnisse der Zielgruppe** eingehen - keine generischen Floskeln.
Format: `"Keyword - Erklaerung (max. 65 Zeichen)"`

**Konsistenz-Regeln (PFLICHT - exakte Formate):**
- Gehaelter: `"3.600 EUR"` (Punkt als Tausendertrennzeichen, Leerzeichen vor EUR, keine Zusaetze wie "ca.")
- Mitarbeiter: `"ca. 950"` oder `"ca. 80-120"` (immer "ca." davor)
- Entfernung: `"3 km"` (Zahl + Leerzeichen + km, kein "ca.")
- SWOT-Titel: max. 35 Zeichen
- SWOT-Text: max. 55 Zeichen
- Bullets: Format `"Keyword - Erklaerung"` oder `"Keyword: Erklaerung"` (erstes Wort fett im Rendering)

---

### Schritt 2 - HTML-Folien generieren (PFLICHT)

Das Skript befindet sich im selben Ordner wie diese SKILL.md unter `scripts/generate_presentation.py`.
**Schritt 2a:** Pfad zum Skript ermitteln:

```bash
SKILL_DIR=$(find /home/ubuntu -name "generate_presentation.py" 2>/dev/null | grep "wettbewerbsanalyse-talent-report" | head -1 | xargs dirname | xargs dirname)
echo "Skill-Verzeichnis: $SKILL_DIR"
```

Falls das Skript nicht gefunden wird, suche nach der SKILL.md:
```bash
SKILL_DIR=$(find /home/ubuntu -name "SKILL.md" 2>/dev/null | xargs grep -l "Talent Report" 2>/dev/null | head -1 | xargs dirname)
echo "Skill-Verzeichnis: $SKILL_DIR"
```

**Schritt 2b:** Skript ausfuehren:

```bash
mkdir -p /home/ubuntu/slides/
python3 "$SKILL_DIR/scripts/generate_presentation.py" \
  /home/ubuntu/research_data.json \
  --html-dir /home/ubuntu/slides/ \
  --project-dir .
```

Wenn du **im Projektordner** arbeitest: `--project-dir .` verwenden. Das Skript laedt das Logo aus diesem Ordner fuer den Footer.

---

### Schritt 3 - ALLE 7 Folien in Manus Slides laden (KEINE ueberspringen!)

`slide_initialize` -> 7 Folien, 1280x720

Dann JEDE Folie einzeln laden - ALLE 7 sind PFLICHT:
1. `/home/ubuntu/slides/slide_01.html` lesen -> `slide_edit` Folie 1 setzen
2. `/home/ubuntu/slides/slide_02.html` lesen -> `slide_edit` Folie 2 setzen
3. `/home/ubuntu/slides/slide_03.html` lesen -> `slide_edit` Folie 3 setzen
4. `/home/ubuntu/slides/slide_04.html` lesen -> `slide_edit` Folie 4 setzen
5. `/home/ubuntu/slides/slide_05.html` lesen -> `slide_edit` Folie 5 setzen
6. `/home/ubuntu/slides/slide_06.html` lesen -> `slide_edit` Folie 6 setzen
7. `/home/ubuntu/slides/slide_07.html` lesen -> `slide_edit` Folie 7 setzen

**STOPP-REGEL:** Exportiere NIEMALS bevor alle 7 Folien per `slide_edit` geladen sind.
Wenn nach Folie 4 oder 5 der Impuls kommt aufzuhoeren: WEITERMACHEN bis Folie 7.

---

### Schritt 4 - Feinkorrektur mit `slide_edit` (NUR Kleinigkeiten!)

**ERLAUBT per `slide_edit`:**
- Textueberlauf fixen (Schrift verkleinern oder Text kuerzen)
- Abstaende/Padding nachjustieren
- Fehlenden Footer ergaenzen
- Positionen leicht verschieben

**VERBOTEN per `slide_edit` (kommt bereits korrekt aus dem Skript!):**
- Radar-SVG auf Folie 3 NICHT veraendern oder ersetzen
  (Entfernungsradar = 3 konzentrische Kreise 40km/20km/Mitte, KEIN Dimensionsradar, KEIN Spinnendiagramm, KEINE Achsen)
- Balkendiagramm auf Folie 4 NICHT umbauen
- SWOT-Kacheln auf Folie 5 NICHT umstrukturieren
- Kartenstruktur auf Folie 2, 6, 7 NICHT neu bauen
- Hintergrundfarben und Farbschema NICHT aendern
- SVGs NICHT komplett neu schreiben
- Den gesamten `<body>`-Inhalt einer Folie NICHT komplett ersetzen

---

### Schritt 5 - Qualitaetspruefung & PDF-Export

**Checkliste (vor Export pruefen):**
- [ ] 7 Folien vorhanden
- [ ] Folie 1: Unternehmensname + Position lesbar, Stadtbild/Standortbild als Hintergrund
- [ ] Folie 2: 3 Karten mit Unternehmensgebaeude oder Logo pro Wettbewerber, Staerke-Box gruen, Schwaeche-Box rot
- [ ] Folie 3: Radar zentriert, 4 Statistik-Karten (Fachkraefte-Pool), Insight-Box
- [ ] Folie 4: 5 Gehaltszeilen links, Balkendiagramm rechts
- [ ] Folie 5: 3 SWOT-Kacheln (gruen/rot/gelb), je 4 Items
- [ ] Folie 6: 3 Chancen-Kacheln (Dienstleistungen aus Pool), je 4 Bullets mit Bold-Keywords
- [ ] Folie 7: 3 Persona-Karten, Schmerzpunkte rot, Werte gruen
- [ ] ALLE: Footer `Talent Report 2026` + Logo, Hintergrund `#e0edc8`
- [ ] KEIN Inhalt ueberlappt den Footer (untere 44px)

Dann **PDF exportieren** und als **direkten Anhang** senden.

---

## Output (verbindlich)

Kurze Zusammenfassung im Text, dann **PDF-Datei als direkter Anhang**.

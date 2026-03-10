---
name: wettbewerbsanalyse-generator-v2
description: "Erstellt vollautomatisierte Wettbewerbsanalysen als 7-Folien-Präsentation im HiOffice-Design (v2.5). CI: #001666 Blau, #EF5800 Orange. Hybrid-Workflow: Python-Skript generiert HTML-Basis, slide_edit für Feinschliff anhand Referenz-PDFs. Output ist eine PDF-Datei als direkter Anhang."
---

# Wettbewerbsanalyse Generator v2.5

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
| Format | 1280x720px (16:9) |

---

## Workflow (verbindlich, in dieser Reihenfolge)

### Schritt 1 - Marktrecherche & JSON erstellen

Recherchiere alle Daten und speichere sie als `/home/ubuntu/research_data.json`.

**Pflicht-Recherchen:**
1. Offizielle Website des Zielunternehmens - Mitarbeiterzahl, Benefits, Tarifvertrag
2. Stellenportale (Indeed, Stepstone, Bundesagentur Entgeltatlas) - Gehalt, offene Stellen
3. **Standortbild Folie 1 (PFLICHT, hohe Aufloesung):** Suche ein **Stadtbild/Panorama des Standorts** in **mind. 1280x720 px** (Wikimedia Commons: `[Stadtname] panorama` oder `[Stadtname] cityscape`, Original oder grosse Vorschau, keine kleinen Thumbnails). Feld: `background_image_url`. Stadtbilder sind immer verfuegbar - leerer String ist NICHT akzeptabel.
4. **Unternehmensgebaeude Folie 2 (PFLICHT, hohe Aufloesung):** Pro Wettbewerber ein Foto des **Unternehmensgebaeudes** in **mind. ca. 800x400 px** (Wikimedia Commons, offizielle Website, keine 250px-Thumbnails). Feld pro Wettbewerber: `building_image_url`. Fallback: Logo (`logo_url` / Clearbit).

Das JSON muss exakt folgendem Schema entsprechen:

```json
{
  "company_name": "Staedtisches Klinikum Braunschweig gGmbH",
  "position": "Pflegefachkraft (m/w/d)",
  "location": "Braunschweig",
  "location_short": "BS",
  "background_image_url": "https://upload.wikimedia.org/wikipedia/commons/.../Braunschweig_panorama.jpg",
  "competitors": [
    {
      "name": "Herzogin Elisabeth Hospital",
      "logo_url": "https://logo.clearbit.com/herzogin-elisabeth-hospital.de",
      "building_image_url": "https://upload.wikimedia.org/wikipedia/commons/.../HEH_Gebaeude.jpg",
      "domain": "herzogin-elisabeth-hospital.de",
      "type": "Kirchlich (Stiftung)",
      "distance": "3 km",
      "employees": "ca. 950",
      "salary": "3.450 EUR",
      "strength": "Kirchliche Werte & familiaere Atmosphaere",
      "weakness": "AVR-Tarif liegt unter TVoeD-P"
    }
  ],
  "regional_stats": [
    {"value": "1.250", "label": "Pflegefachkraefte im 40-km-Umkreis (verfuegbar/wechselwillig)"},
    {"value": "14", "label": "Krankenhaeuser im 40-km-Radius"},
    {"value": "320", "label": "Davon aktiv stellensuchend (Zielposition)"},
    {"value": "-8%", "label": "Rueckgang verfuegbarer Fachkraefte seit 2022"}
  ],
  "regional_insight": "Vollstaendiger Insight-Satz mit regionalem Kontext.",
  "salaries": [
    {"name": "Zielunternehmen", "salary": "3.600 EUR", "bar_color": "#EF5800"},
    {"name": "Wettbewerber 1", "salary": "3.550 EUR", "bar_color": "#001666"},
    {"name": "Wettbewerber 2", "salary": "3.450 EUR", "bar_color": "#001666"},
    {"name": "Wettbewerber 3", "salary": "3.400 EUR", "bar_color": "#001666"},
    {"name": "Durchschnitt Bundesland (Pflege)", "salary": "3.320 EUR", "bar_color": "#aaa", "is_average": true}
  ],
  "swot": [
    {
      "title": "STAERKEN", "color": "#27AE60", "icon": "check",
      "points": [
        {"title": "Titel max. 35 Zeichen", "text": "Keyword - Erklaerung max. 55 Zeichen"}
      ]
    },
    {"title": "SCHWAECHEN", "color": "#E74C3C", "icon": "warning", "points": [{"title": "...", "text": "..."}]},
    {"title": "RISIKEN", "color": "#EF5800", "icon": "risk", "points": [{"title": "...", "text": "..."}]}
  ],
  "opportunities": [
    {
      "title": "[DIENSTLEISTUNG AUS POOL - passend zur Branche]", "color": "#4A90D9", "icon": "star",
      "bullets": [
        "Keyword - Erklaerung passend zur Schwaeche des Wettbewerbers",
        "Keyword - Erklaerung passend zur Zielgruppe",
        "Keyword - Konkrete Leistung von HiOffice",
        "Keyword - Messbarer Nutzen fuer den Kunden"
      ]
    },
    {
      "title": "[DIENSTLEISTUNG AUS POOL - passend zur Branche]", "color": "#27AE60", "icon": "target",
      "bullets": ["...", "...", "...", "..."]
    },
    {
      "title": "[DIENSTLEISTUNG AUS POOL - passend zur Branche]", "color": "#EF5800", "icon": "mobile",
      "bullets": ["...", "...", "...", "..."]
    }
  ],
  "personas": [
    {
      "name": "Thomas, 34", "archetype": "Erfahrener Pflegefachmann - 8 Jahre",
      "color": "#EF5800",
      "pain_points": ["Keyword - Erklaerung (max. 55 Zeichen)"],
      "values": ["Keyword - Erklaerung (max. 55 Zeichen)"]
    }
  ]
}
```

**Recherche-Regeln:**
- Genau 3 Wettbewerber im 30-50 km Radius, keine Tochtergesellschaften des Zielunternehmens
- Pro Wettbewerber: staerkstes Argument + Schwaeche (PFLICHT)
- Genau 4 `regional_stats` (2 links, 2 rechts auf Folie 3) - PFLICHT: Alle 4 Werte beziehen sich auf die **verfuegbaren Personen mit dem Stellentitel** (Fachkraefte-Pool) im 40-km-Umkreis, NICHT auf offene Stellen. Beispiele: Anzahl Fachkraefte mit dem Stellentitel in der Region, davon aktiv stellensuchend/wechselwillig, Anzahl Arbeitgeber in der Branche im Umkreis, Trend (Rueckgang/Zuwachs) verfuegbarer Fachkraefte.
- Genau 5 `salaries` (Zielunternehmen + 3 Wettbewerber + Landes-Durchschnitt mit `"is_average": true`)
- Genau 3 SWOT-Kategorien mit je 4 Punkten
- Genau 3 Chancen mit je 4 Bullets
- Genau 3 Personas mit je 3 Schmerzpunkten + 3 Werten

**Bilder (PFLICHT):**
- **Folie 1 - Titelfolie:** `background_image_url`: **Stadtbild/Panorama des Standorts** (Wikimedia Commons: `[Stadtname] panorama` oder `[Stadtname] cityscape`). **PFLICHT - darf NICHT leer sein.** Stadtbilder sind immer verfuegbar.
- **Folie 2 - Wettbewerber-Karten:** Pro Wettbewerber `building_image_url`: Foto des **Unternehmensgebaeudes** (Wikimedia Commons, offizielle Website). Fallback im Skript: Logo. Prioritaet Logo, wenn kein Gebaeude:
  1. `logo_url` oder `https://logo.clearbit.com/[domain]`
  2. Logo von der offiziellen Website
  3. Leer - Skript zeigt Initialen-Platzhalter
  **PFLICHT:** `domain` immer befuellen (z.B. `"klinikum-braunschweig.de"`), damit Clearbit-Fallback funktioniert.

**Bildqualitaet (PFLICHT - keine verpixelten Bilder):**
- Alle Bild-URLs muessen eine **ausreichende Aufloesung** haben, damit die Darstellung scharf wirkt.
- **Folie 1 (Hintergrund, Vollbild 1280x720 px):** Mindestens **1280x720 px**, idealerweise groesser (z.B. 1920x1080). Bei Wikimedia Commons: Link auf **Original** oder grosse Vorschau waehlen; **keine** kleinen Thumbnail-URLs (z.B. .../thumb/.../250px-... oder 500px-...). Stattdessen die Datei-URL in Originalgroesse oder z.B. `1280px-`-Vorschau verwenden.
- **Folie 2 (Wettbewerber-Karten, ca. 400x120 px sichtbar):** Pro Gebaeude-Foto mindestens **ca. 800x400 px** (besser 800x600 oder mehr), damit beim Beschneiden keine Verpixelung entsteht. Bei Wikimedia: mittlere bis grosse Aufloesung waehlen (z.B. 800px- oder 1000px- Vorschau), keine 200px-/250px-Thumbnails.
- **Allgemein:** Immer die **groesste sinnvoll verfuegbare** Version verlinken; bei Unsplash/Wikimedia Original pruefen. Lieber eine Quelle mit hoher Aufloesung waehlen als eine niedrige.

**Chancen (opportunities) - PFLICHT: HiOffice-Dienstleistungen dynamisch auswaehlen:**
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

**Auswahlregel:** Branchenspezifische Dienstleistungen (`PFLEGEPERSONAL FINDEN`, `MITARBEITER FINDEN IM HANDWERK`) haben Vorrang wenn sie zur Zielgruppe passen. Ergaenze mit allgemeinen Dienstleistungen bis du 3 hast.

**Bullets-Regel:** Die Bullets jeder Karte muessen konkret auf die **Schwaechen des analysierten Wettbewerbers** und die **Beduerfnisse der Zielgruppe** eingehen - keine generischen Floskeln.
Format: `"Keyword - Erklaerung (max. 65 Zeichen)"`

**Konsistenz-Regeln (PFLICHT - exakte Formate):**
- Gehaelter: `"3.600 EUR"` (Punkt als Tausendertrennzeichen, Leerzeichen vor EUR, keine Zusaetze wie "ca.")
- Mitarbeiter: `"ca. 950"` (immer "ca." davor, keine Einheit "Mitarbeiter")
- Entfernung: `"3 km"` (Zahl + Leerzeichen + km, kein "ca.")
- SWOT-Titel: max. 35 Zeichen - bei Ueberschreitung kuerzen
- SWOT-Text: max. 55 Zeichen - bei Ueberschreitung kuerzen
- Bullets: Format `"Keyword - Erklaerung"` oder `"Keyword: Erklaerung"` (erstes Wort fett im Rendering)

---

### Schritt 2 - HTML-Folien generieren (PFLICHT - kein manuelles HTML von Grund auf!)

```bash
mkdir -p /home/ubuntu/slides/
python3 /home/ubuntu/skills/wettbewerbsanalyse-generator-v2/scripts/generate_presentation.py \
  /home/ubuntu/research_data.json \
  --html-dir /home/ubuntu/slides/
```

Das Skript:
1. Laedt alle Bilder automatisch herunter und bettet sie als base64 ein
2. Generiert 7 HTML-Dateien (1280x720px, 16:9) in `/home/ubuntu/slides/`

**WICHTIG:** HTML-Grundgeruest IMMER ueber das Skript erzeugen, niemals komplett manuell schreiben.

---

### Schritt 3 - ALLE 7 Folien in Manus Slides laden (KEINE ueberspringen!)

```
slide_initialize  ->  7 Folien, Format 1280x720
```

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
- [ ] Folie 5: 3 SWOT-Kacheln (gruen/rot/orange), je 4 Items
- [ ] Folie 6: 3 Chancen-Kacheln (HiOffice-Dienstleistungen), je 4 Bullets mit Bold-Keywords
- [ ] Folie 7: 3 Persona-Karten, Schmerzpunkte rot, Werte gruen
- [ ] ALLE: Footer `@HiOffice Group 2026` + Logo, Hintergrund `#001666`
- [ ] KEIN Inhalt ueberlappt den Footer (untere 44px)

Dann als **PDF exportieren** und als **direkten Anhang** senden

---

## Output (verbindlich)

Kurze Zusammenfassung der wichtigsten Erkenntnisse (3-5 Saetze) im Text, dann **PDF-Datei als direkter Anhang** - keine Links, keine Viewer-URLs.

# Projektkontext: Automatisierte KI-Analysen für Sales

## 1. Projektziel

Entwicklung eines Microsoft Teams-Chatbots, der Sales-Briefings entgegennimmt, automatisch normalisiert und an den KI-Agenten **Manus.ai** weiterleitet. Manus erstellt daraus eine vollautomatisierte **Wettbewerbsanalyse-Präsentation** (7 Folien, High Office Design), die der Bot anschließend an den Absender in Teams zurücksendet.

**Kernproblem, das gelöst wird:** Vertriebsmitarbeiter müssen nach jedem Sales Call manuell eine Wettbewerbsanalyse erstellen – inklusive Recherche zu Gehältern, Wettbewerbern und regionalem Arbeitsmarkt. Die Automatisierung spart pro Briefing 1–3 Stunden manueller Arbeit.

---

## 2. Anwendungsfall & Branchenkontext

### Unternehmen
**High Office IT GmbH** – Personalvermittlung / Recruiting mit Fokus auf soziale und pflegerische Berufe (Heilerziehungspfleger, Pflegefachkräfte, Erzieher etc.)

### Typischer Workflow
1. Vertriebler führt Erstgespräch mit einem Pflegeträger (z.B. DRK, Diakonie, AWO)
2. Notiert Pain Points: Fachkräftemangel, Rentenwelle, Ghosting, Agenturversagen etc.
3. Schickt Briefing per Teams an den `@SalesBot`
4. Bot normalisiert den Input und extrahiert die 3 Pflichtfelder (Unternehmen, Standort, Position)
5. Manus erstellt autonom eine Wettbewerbsanalyse (Recherche + SWOT + Gehälter + Personas)
6. Vertriebler erhält die fertige Präsentation in Teams und nutzt sie im Folgegespräch

### Zielnutzer
Vertriebsteam (initial 1–5 Personen) innerhalb einer Microsoft Teams-Umgebung.

---

## 3. Input-Formate

Der Bot akzeptiert zwei Arten von Input, die automatisch erkannt werden:

### Modus A: „Rich Input" – Detaillierte Gesprächsnotizen

Freitext mit ausführlichen Pain Points, Evidenzen und Kontext aus einem Sales Call.

**Beispiel:**
```
Deutsches Rotes Kreuz Kreisverband Lausitz e. V.

2-3 HEPs
Müssen wachsen
Viele gehen noch in Rente
Lange keinen mehr eingestellt
2-3 Unqualifizierte BW

Heilerziehungspfleger-Mangel: 2-3 geplante Einstellungen + Rentenwelle (3 MA gleichzeitig)
Rekrutierungsversagen bisheriger Agenturen: 2-3 unqualifizierte Bewerber, keine Einstellung in 3 Monaten
Hoher Krankenstand
Schichtmodell-Resistenz: Bewerber lehnen Schichten/Wochenenden ab
Ghosting: Bewerber sagen kurzfristig ab
Geografische Isolation: Lausitz, 55 km zu Dresden, 100+ km zu Berlin

Strukturell:
- 460 Mitarbeiter, 20+ Einrichtungen
- Arbeitet bereits mit Arbeitnehmerüberlassung
- Schulische Ausbildung nicht ausreichend
```

### Modus B: „Minimal Input" – Strukturierte Basisdaten

Kompakte Angaben, aus denen Manus eigenständig recherchiert und die Analyse erstellt.

**Beispiel:**
```
Deutsches Rotes Kreuz Kreisverband Lausitz e. V.
PFKs
Lausitz
https://www.drk-lausitz.de
```

**Felder bei Minimal Input:**
| Feld | Pflicht | Beschreibung |
|------|---------|--------------|
| Unternehmen | Ja | Name des Trägers/Unternehmens |
| Zielgruppe | Ja | Berufsgruppe (HEP, PFK, Erzieher etc.) |
| Standort | Ja | Stadt, Region oder Bundesland |
| URL | Nein | Website des Unternehmens |

---

## 4. Manus.ai – Konfiguration & Skill

### Systemprompt (in Manus hinterlegt)

Manus ist als Projekt mit folgendem Kontext konfiguriert:

- **Systemprompt**: „WETTBEWERBSANALYSE HIGH OFFICE 5.0"
- **Skill**: `wettbewerbsanalyse-generator` (als Manus-Skill deployed)
- **Referenz-Präsentation**: Vorlage im Manus-Projektkontext (`.pptx`)
- **CI-Logo**: `Hioffice_logo_white.svg` im Footer jeder Folie

### Was Manus autonom erledigt

1. **Referenz-PDF analysieren** – Design-Parameter extrahieren (Farben, Fonts, Layouts)
2. **Skill-Workflow ausführen**:
   - Briefing auswerten (Unternehmen, Standort, Position)
   - Web-Recherche: Wettbewerber, Gehälter (P25/Median/P75), Fachkräftepool, Gebäudebilder
   - SWOT-Analyse ableiten
   - 3 Recruiting-Personas entwickeln
   - 7-Folien-Präsentation generieren
   - Sprecher-Notizen hinzufügen

### Manus Input-Format (Ziel der Normalisierung)

Der Bot muss den User-Input in dieses Format überführen:

```
Erstelle eine Wettbewerbsanalyse für:

**Unternehmen:** [Name + Rechtsform]
**Standort:** [Stadt, Bundesland]
**Position:** [Berufsbezeichnung]
```

**Beispiel:**
```
Erstelle eine Wettbewerbsanalyse für:

**Unternehmen:** Deutsches Rotes Kreuz Kreisverband Lausitz e.V.
**Standort:** Lausitz, Brandenburg
**Position:** Heilerziehungspfleger
```

Bei Rich Input können optional zusätzliche Kontextdaten angehängt werden:
```
Erstelle eine Wettbewerbsanalyse für:

**Unternehmen:** Deutsches Rotes Kreuz Kreisverband Lausitz e.V.
**Standort:** Lausitz, Brandenburg
**Position:** Heilerziehungspfleger

**Zusätzlicher Kontext aus dem Erstgespräch:**
- 2-3 HEP-Stellen geplant, Rentenwelle (3 MA gehen gleichzeitig)
- Bisherige Agenturen liefern nur unqualifizierte Bewerber
- 460 Mitarbeiter, 20+ Einrichtungen
- Arbeitet bereits mit Arbeitnehmerüberlassung
- Geografische Isolation: 55 km zu Dresden, 100+ km zu Berlin
```

### Manus Output

| Folie | Inhalt |
|-------|--------|
| 1 | **Titelfolie**: „Wettbewerbs-Analyse" + Unternehmensname |
| 2 | **Lokaler Wettbewerb**: 3 Karten (Name, Typ, Entfernung, Teamgröße, Gehalt) |
| 3 | **Regionale Analyse**: Fachkräftepool + Einrichtungen im Radius |
| 4 | **Gehaltsanalyse**: Horizontaler Balken mit Callout-Boxen (P25/Median/P75) |
| 5 | **SWOT-Analyse**: Stärken, Schwächen, Risiken (je 3–4 Punkte) |
| 6 | **Chancen**: 3 strategische Handlungsempfehlungen |
| 7 | **Personas**: 3 Recruiting-Personas (Archetyp, Pain Points, Werte, Kernzitat) |

### Design-System (High Office Branding)

```
Hintergrund:     #2C3E50 (dunkles Blaugrau, alle Folien)
Text hell:       #ECF0F1
Akzent:          #E67E22 (Orange)
Karten:          #FFFFFF, Border-Radius 8px, Shadow 0 4px 12px
Schrift:         Roboto (Google Fonts)
Foliengröße:     1280 × 720px (16:9)
Footer:          „@High Office IT GmbH 2026" + Logo
```

---

## 5. Normalisiertes Datenmodell

### Kern-Felder (Pflicht für Manus)

```json
{
  "unternehmen": "Deutsches Rotes Kreuz Kreisverband Lausitz e.V.",
  "standort": "Lausitz, Brandenburg",
  "position": "Heilerziehungspfleger"
}
```

### Erweitertes Modell (intern für Tracking + optionaler Kontext)

```json
{
  "manus_prompt": {
    "unternehmen": "Deutsches Rotes Kreuz Kreisverband Lausitz e.V.",
    "standort": "Lausitz, Brandenburg",
    "position": "Heilerziehungspfleger",
    "zusatzkontext": "2-3 Stellen geplant, Rentenwelle, Agenturversagen..."
  },
  "meta": {
    "input_modus": "rich",
    "erstellt_von": "david.jekal@highoffice.de",
    "erstellt_am": "2026-02-18T14:30:00Z",
    "teams_user_id": "...",
    "teams_conversation_id": "...",
    "manus_task_id": null,
    "status": "validiert"
  }
}
```

---

## 6. Systemarchitektur

```
┌──────────────────────────────────────────────────────────────────┐
│                    Microsoft Teams                                │
│                                                                  │
│  Teams-Gruppe "Sales Briefings"                                  │
│  ┌──────────────────────────────────────────────────────┐        │
│  │ @SalesBot DRK Lausitz, HEP, Lausitz                  │        │
│  │                                                      │        │
│  │ Bot: Erkannt:                                         │        │
│  │   Unternehmen: DRK Kreisverband Lausitz e.V.         │        │
│  │   Position: Heilerziehungspfleger                     │        │
│  │   Standort: Lausitz, Brandenburg                      │        │
│  │   → Wettbewerbsanalyse wird erstellt...               │        │
│  └──────────────────────────────────────────────────────┘        │
│                         │                         ▲              │
│                         │ Nachricht               │ Präsentation │
└─────────────────────────┼─────────────────────────┼──────────────┘
                          │                         │
                          ▼                         │
┌─────────────────────────────────────────────────────────────────┐
│                 Backend (Render Web Service)                      │
│                                                                  │
│  FastAPI Application                                             │
│  ├── POST /api/teams/messages     ← Teams Bot Endpoint           │
│  ├── POST /api/manus/webhook      ← Manus Completion Callback   │
│  └── GET  /health                 ← Health Check                 │
│                                                                  │
│  Interne Module:                                                 │
│  ┌─────────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ Input Processor  │  │ Manus Client  │  │ Teams Bot Logic  │   │
│  │                 │  │               │  │                  │   │
│  │ - Modus-        │  │ - POST /tasks │  │ - Konversation   │   │
│  │   Erkennung     │  │ - GET /tasks  │  │ - Rückfragen     │   │
│  │ - 3 Felder      │  │ - Webhook-    │  │ - Proactive Msg  │   │
│  │   extrahieren   │  │   Handler     │  │ - File Delivery  │   │
│  │ - Validierung   │  │ - File        │  │   (Graph API)    │   │
│  │ - Manus-Prompt  │  │   Download    │  │                  │   │
│  │   generieren    │  │               │  │                  │   │
│  └────────┬────────┘  └───────┬───────┘  └────────┬─────────┘   │
│           │                   │                    │             │
│           ▼                   │                    │             │
│  ┌─────────────────┐          │                    │             │
│  │   Database      │          │                    │             │
│  │  (PostgreSQL)   │          │                    │             │
│  └─────────────────┘          │                    │             │
└───────────────────────────────┼────────────────────┼─────────────┘
                                │                    │
                                ▼                    │
┌─────────────────────────────────────────────────────────────────┐
│                  Manus.ai (Projekt)                               │
│                                                                  │
│  Systemprompt: "WETTBEWERBSANALYSE HIGH OFFICE 5.0"             │
│  Skill: wettbewerbsanalyse-generator                            │
│  Assets: Referenz-Präsentation (.pptx) + Logo (.svg)            │
│                                                                  │
│  Input:  "Erstelle eine Wettbewerbsanalyse für:                  │
│           Unternehmen: ... | Standort: ... | Position: ..."      │
│                                                                  │
│  Autonom: Recherche → SWOT → Gehälter → Personas → 7 Folien    │
│                                                                  │
│  Output: Präsentation (Slides) + Sprecher-Notizen               │
│  Webhook → task_stopped                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Tech-Stack

| Komponente | Technologie | Begründung |
|---|---|---|
| **Sprache** | Python 3.11+ | Beste LLM-Library-Unterstützung, schnelle Entwicklung |
| **Web Framework** | FastAPI | Async-fähig, auto-generierte API-Docs, Pydantic-Integration |
| **Teams SDK** | botbuilder-python (Bot Framework SDK) | Offizielle Microsoft-Library für Python Teams-Bots |
| **LLM (Normalisierung)** | OpenAI API (GPT-4o) oder Anthropic (Claude) | Entity-Extraction und Freitext-Klassifikation |
| **Manus Integration** | HTTP Client (httpx) | Direkte REST-API-Aufrufe an Manus |
| **Datenbank** | PostgreSQL (Render) oder SQLite (lokal) | Task-Status, Conversation-State, User-Mapping |
| **ORM** | SQLAlchemy + Alembic | Datenbankzugriff und Migrationen |
| **Hosting** | Render (Web Service) | Einfaches Deployment, günstiges Hosting, HTTPS inklusive |
| **Bot-Registrierung** | Azure AD (App Registration) | Pflicht für jeden Teams-Bot, kostenlos |

---

## 8. Projektstruktur

```
automatisierte_KI_Analysen_Sales/
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI App, Router-Einbindung
│   ├── config.py                    # Pydantic Settings (ENV-Variablen)
│   │
│   ├── input_processor/
│   │   ├── __init__.py
│   │   ├── classifier.py            # Erkennung: Rich vs. Minimal Input
│   │   ├── extractor.py             # LLM-basierte Entity-Extraktion
│   │   ├── validator.py             # Pflichtfeld-Prüfung, Rückfrage-Logik
│   │   └── prompts.py               # System-Prompts für LLM-Aufrufe
│   │
│   ├── manus/
│   │   ├── __init__.py
│   │   ├── client.py                # Manus REST-API Client
│   │   ├── webhook_handler.py       # Eingehende Manus-Webhooks verarbeiten
│   │   └── schemas.py               # Pydantic-Modelle für Manus API
│   │
│   ├── teams/
│   │   ├── __init__.py
│   │   ├── bot.py                   # Teams ActivityHandler (Konversationslogik)
│   │   ├── messages.py              # Endpoint für Teams-Nachrichten
│   │   └── file_sender.py           # Dateiversand per Graph API / DM
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                  # SQLAlchemy-Modelle: Task, User, Conversation
│   │
│   └── database.py                  # DB-Engine, Session-Management
│
├── alembic/                         # Datenbank-Migrationen
│   └── ...
│
├── tests/
│   ├── test_classifier.py
│   ├── test_extractor.py
│   ├── test_validator.py
│   ├── test_manus_client.py
│   └── test_bot.py
│
├── .env.example                     # Vorlage für Umgebungsvariablen
├── .gitignore
├── requirements.txt
├── render.yaml                      # Render Deployment-Konfiguration
└── PROJEKTKONTEXT.md                # Dieses Dokument
```

---

## 9. Umgebungsvariablen

```env
# LLM
OPENAI_API_KEY=sk-...                          # Für Input-Normalisierung

# Manus
MANUS_API_KEY=...                              # Manus API-Zugang
MANUS_API_BASE_URL=https://api.manus.ai/v1    # Manus API Basis-URL
MANUS_WEBHOOK_SECRET=...                       # Zur Verifizierung eingehender Webhooks

# Teams / Azure
MICROSOFT_APP_ID=...                           # Azure AD App Registration
MICROSOFT_APP_PASSWORD=...                     # Azure AD Client Secret

# Datenbank
DATABASE_URL=postgresql://user:pass@host/db    # Render PostgreSQL oder lokal SQLite

# Allgemein
ENVIRONMENT=development                        # development | production
LOG_LEVEL=INFO
```

---

## 10. API-Endpunkte

### Intern (FastAPI)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `POST` | `/api/teams/messages` | Teams Bot Framework Messaging-Endpoint |
| `POST` | `/api/manus/webhook` | Eingehende Manus-Webhooks (Task fertig) |
| `GET` | `/health` | Health Check für Render |
| `GET` | `/api/tasks/{task_id}` | Task-Status abfragen (intern/Debug) |

### Externe APIs (ausgehend)

| Service | Endpunkt | Zweck |
|---------|----------|-------|
| Manus | `POST /v1/tasks` | Neuen Task erstellen |
| Manus | `GET /v1/tasks/{id}` | Task-Status prüfen |
| Manus | `POST /v1/webhooks` | Webhook registrieren |
| Manus | `POST /v1/files` | Dateien hochladen |
| OpenAI | `POST /v1/chat/completions` | Input-Normalisierung |
| Microsoft Graph | Diverse Endpunkte | Datei-Upload, proaktive Nachrichten |

---

## 11. Konversationsflow

### Szenario 1: Vollständiger Rich Input

```
User:    @SalesBot DRK Kreisverband Lausitz e.V.
         2-3 HEPs, Lausitz, Rentenwelle, Agenturversagen...
         460 MA, 20+ Einrichtungen, arbeiten mit Leiharbeit

Bot:     Wettbewerbsanalyse-Briefing erkannt:

         Unternehmen: DRK Kreisverband Lausitz e.V.
         Position:    Heilerziehungspfleger (HEP)
         Standort:    Lausitz, Brandenburg

         Zusatzkontext: 6 Pain Points erkannt
         (Rentenwelle, Agenturversagen, Ghosting, ...)

         Wettbewerbsanalyse wird erstellt...
         Geschätzte Dauer: 10–15 Minuten.

Bot:     @User Deine Wettbewerbsanalyse für DRK Kreisverband
(DM)     Lausitz ist fertig!
         [Wettbewerbsanalyse_DRK_Lausitz_HEP.pdf]
```

### Szenario 2: Minimal Input mit Rückfrage

```
User:    @SalesBot DRK Lausitz, Pfleger

Bot:     Erkannt: DRK Lausitz
         "Pfleger" ist mehrdeutig. Meinst du:
         1. Pflegefachkraft (PFK)
         2. Heilerziehungspfleger (HEP)
         3. Pflegehelfer / Pflegeassistent

User:    2

Bot:     Unternehmen: DRK Lausitz
         Position:    Heilerziehungspfleger (HEP)
         Standort:    Lausitz

         Wettbewerbsanalyse wird erstellt...
```

### Szenario 3: Unvollständiger Input

```
User:    @SalesBot DRK Lausitz

Bot:     Erkannt: DRK Lausitz
         Welche Position soll analysiert werden?
         (z.B. Heilerziehungspfleger, Pflegefachkraft, Erzieher)

User:    HEP

Bot:     Unternehmen: DRK Lausitz
         Position:    Heilerziehungspfleger (HEP)
         Standort:    Lausitz

         Wettbewerbsanalyse wird erstellt...
```

### Szenario 4: Komplett-Input (kein Rückfragen nötig)

```
User:    @SalesBot
         Erstelle eine Wettbewerbsanalyse für:
         Unternehmen: Sanssouci Pflege GmbH
         Standort: Potsdam, Brandenburg
         Position: Pflegefachkraft

Bot:     Unternehmen: Sanssouci Pflege GmbH
         Position:    Pflegefachkraft
         Standort:    Potsdam, Brandenburg

         Wettbewerbsanalyse wird erstellt...
```

---

## 12. Zielgruppen-Taxonomie (Berufsgruppen)

Der Input-Processor muss Abkürzungen und Synonyme korrekt auflösen:

| Eingabe (Varianten) | Normalisiert | Manus-Position |
|---------------------|-------------|----------------|
| HEP, Heilerziehungspfleger | Heilerziehungspfleger (HEP) | Heilerziehungspfleger |
| PFK, Pflegefachkraft, exam. Pflegekraft | Pflegefachkraft (PFK) | Pflegefachkraft |
| Erzieher, Erzieherin | Erzieher/in | Erzieher |
| AP, Altenpfleger, Altenpflegerin | Altenpfleger/in | Altenpfleger |
| OTA, OP-Pflege | OTA / OP-Pflegekraft | OTA |
| Sozialarbeiter, Sozialpädagoge | Sozialarbeiter/in | Sozialarbeiter |
| „Pfleger", „Pflege" | **MEHRDEUTIG** → Rückfrage | – |

Diese Liste wird im Input-Processor als Lookup-Tabelle hinterlegt und kann erweitert werden.

---

## 13. Umsetzungsphasen

### Phase 1: Backend-Grundgerüst ⏱️ ~2-3 Stunden
- [ ] Python-Projekt aufsetzen (FastAPI, Dependencies)
- [ ] Pydantic-Konfiguration (.env-Handling)
- [ ] Datenmodell definieren (SQLAlchemy)
- [ ] Health-Endpoint
- [ ] Input-Processor: Klassifikation + Extraktion + Validierung
- [ ] Unit-Tests für Input-Processor

### Phase 2: Manus-Integration ⏱️ ~2-3 Stunden
- [ ] Manus API Client (Task erstellen, Status abfragen)
- [ ] Webhook-Endpoint + Signatur-Verifizierung
- [ ] Datei-Download von Manus
- [ ] End-to-End-Test: HTTP-Request → Manus-Task → Ergebnis

### Phase 3: Teams-Bot ⏱️ ~3-4 Stunden
- [ ] Bot Framework Integration (ActivityHandler)
- [ ] Messaging-Endpoint für Teams
- [ ] Konversationslogik (Rückfragen, Bestätigungen)
- [ ] Proaktiver Datei-Rückversand
- [ ] Conversation-State-Management

### Phase 4: Deployment ⏱️ ~1-2 Stunden
- [ ] Render-Konfiguration (render.yaml)
- [ ] PostgreSQL auf Render einrichten
- [ ] Azure AD App Registration (manueller Schritt)
- [ ] Bot im Teams Kanal aktivieren
- [ ] End-to-End-Test in Produktion

---

## 14. Bekannte Einschränkungen & Risiken

| Risiko | Beschreibung | Mitigation |
|--------|-------------|------------|
| Manus-Laufzeit | Task-Ausführung kann 5–30 Min dauern | Statusupdates an User senden |
| Manus-Fehler | Task könnte fehlschlagen | Retry-Logik + Fehlermeldung an User |
| LLM-Halluzination | Falsche Entity-Extraktion | Bestätigungsschritt vor Manus-Übergabe |
| Teams File-Upload | Graph API erfordert spezielle Permissions | Fallback: Datei als Link senden |
| Rate Limits | Manus/OpenAI API-Limits | Queuing-Mechanismus |
| Kosten | LLM-Aufrufe pro Briefing | Monitoring + Budget-Alerts |

---

## 15. Kosten (geschätzt)

| Posten | Kosten/Monat | Anmerkung |
|--------|-------------|-----------|
| Render Web Service | $7 | Starter Plan (immer an) |
| Render PostgreSQL | $7 | Optional, empfohlen |
| OpenAI API | ~$5–15 | Ca. $0.01–0.05 pro Briefing |
| Manus API | Abhängig vom Plan | Prüfen: inkl. im Manus-Abo? |
| Azure AD | $0 | App Registration ist kostenlos |
| **Gesamt** | **~$20–30** | Bei moderater Nutzung |

---

## 16. Beispiel: Manus-Output (DRK Lausitz, HEP)

Validiert anhand der echten Präsentation `Wettbewerbsanalyse_DRK_Lausitz.pptx`:

| Folie | Inhalt |
|-------|--------|
| 1 – Titel | „WETTBEWERBS-ANALYSE" – DRK-Kreisverband Lausitz e.V. |
| 2 – Lokaler Wettbewerb | Lausitzer Werkstätten (25km, 300+ MA, 3.600€), Johanniter Südbrandenburg (30km, 200 MA, 3.750€), Diakonisches Werk Niederlausitz (20km, 250 MA, 3.700€) |
| 3 – Regionale Analyse | ~400–800 HEP-Fachkräfte im 40km-Radius, 15–25 Einrichtungen der Eingliederungshilfe |
| 4 – Gehaltsanalyse | Unternehmen 3.700€ vs. Wettbewerber (3.600€–3.750€ Spanne) |
| 5 – SWOT | Stärken: 460 MA, Bildungszentrum, DRK-Marke. Schwächen: Randlage, Rentenwelle, Krankenstand. Risiken: Berlin-Sog (+10–15% Gehalt), 89 offene HEP-Stellen, Ghosting |
| 6 – Chancen | Direktansprache (Potsdam/Dresden/Cottbus), Ausbildungs-Exit (Übernahme), Employer Branding |
| 7 – Personas | Sandra 42 „Die Heimatverbundene", Tim 26 „Der Berufseinsteiger", Katrin 38 „Die Rückkehrerin" – jeweils mit Schmerzpunkten + Werten |

**Bestätigt:** Manus integriert Pain Points aus dem Rich Input direkt in die SWOT-Analyse (Rentenwelle, Ghosting, Schichtmodell-Resistenz erscheinen alle in der Präsentation).

---

## 17. Geklärte Entscheidungen

| Entscheidung | Ergebnis |
|---|---|
| Hosting | Render (Web Service $7/Monat) |
| Input-Kanal | Microsoft Teams Chatbot in einer Gruppe |
| Rückkanal | DM an den Absender mit der fertigen Präsentation |
| Manus-Skill | `wettbewerbsanalyse-generator` – bereits konfiguriert |
| Manus-Input | 3 Pflichtfelder: Unternehmen, Standort, Position + optionaler Zusatzkontext |
| Manus-Output | 7-Folien-Präsentation (pptx) im High Office Design |
| Rich Input → Manus | Pain Points werden als Zusatzkontext an den Manus-Prompt angehängt |
| Design | High Office Branding (#2C3E50 / #E67E22 / Roboto) |

## 18. Offene Entscheidungen

- [ ] Welches LLM für die Input-Normalisierung? (OpenAI GPT-4o vs. Claude)
- [ ] Manus API-Zugang: Key vorhanden? Wie wird der Skill per API getriggert?
- [ ] Bestätigungsschritt: Bot zeigt Zusammenfassung und wartet auf „Go", oder direkt loslegen?
- [ ] Berufsgruppen-Liste: Sind die in Abschnitt 12 aufgeführten Gruppen vollständig?

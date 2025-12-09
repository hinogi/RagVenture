# AI-Textadventure - Setup & Installation

Ein textbasiertes Adventure-Game mit Neo4j GraphDB und Rich Terminal UI.

**Tech-Stack:** Python, Neo4j, Rich, (später: Ollama)

---

## 📋 Voraussetzungen

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Git** (optional, für Versionskontrolle)

---

## 🚀 Installation

### 1. Docker Desktop installieren

**Windows/Mac:**
1. Download von https://www.docker.com/products/docker-desktop/
2. Installieren und starten
3. Testen: `docker --version`

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo systemctl start docker
```

### 2. Neo4j Container starten

```bash
# Container erstellen und starten
docker run -d \
    --name textadventure-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j_data:/data \
    neo4j:latest
```

**Was passiert:**
- Port `7474`: Web UI → http://localhost:7474
- Port `7687`: Bolt Protocol (für Python)
- Volume `neo4j_data`: Daten bleiben bei Restart erhalten
- Login: `neo4j` / `password`

**Neo4j Browser testen:**
1. Öffne http://localhost:7474
2. Login: `neo4j` / `password`
3. Teste Query: `RETURN "Hello Neo4j" AS message`

### 3. Python Environment einrichten

```bash
# Repository klonen (oder Ordner erstellen)
git clone <repo-url>
cd textadventure

# Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# spaCy Sprachmodelle herunterladen
python -m spacy download de_core_news_lg      # Großes klassisches Model (560MB)
python -m spacy download de_dep_news_trf       # Transformer-basiert (500MB)
```

**`requirements.txt`:**
```
rich>=13.0.0
neo4j>=5.0.0
python-dotenv>=1.0.0
jupyter>=1.0.0
sentence-transformers>=3.0.0
spacy>=3.8.0

# spaCy Models (install separately):
# python -m spacy download de_core_news_lg
# python -m spacy download de_dep_news_trf
```

**Hinweis:** Die spaCy Models werden separat heruntergeladen und können je nach Bedarf gewählt werden:
- `de_core_news_lg` - CNN-basiert, schnell, ~560MB
- `de_dep_news_trf` - Transformer-basiert (BERT), beste Genauigkeit, ~500MB

### 4. Environment Variables konfigurieren

```bash
# .env Datei erstellen (aus Template)
cp .env.example .env

# .env bearbeiten und Credentials eintragen:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 5. Spielwelt in Neo4j initialisieren

```bash
# Jupyter Notebook starten
jupyter notebook

# Im Browser: notebooks/01-neo4j_dbsetup.ipynb öffnen
# Alle Zellen nacheinander ausführen (Cell → Run All)
```

**Was das Notebook macht:**
- Erstellt Constraints für eindeutige IDs (Location, Item, NPC, Player)
- Erstellt Performance-Indexes
- Generiert die Spielwelt (4 Locations, 8 Items, 3 NPCs)
- Verknüpft alles mit Relationships
- Erstellt Embeddings für alle Entities (name + description)

**Bei Problemen / Neustart:**
```python
# Alle Daten löschen (nur wenn nötig!)
MATCH (n) DETACH DELETE n

# Dann Notebook erneut komplett durchlaufen
```

---

## 🗂️ Projektstruktur

```
RagVenture/
├── src/
│   ├── controller/
│   │   └── game_controller.py    # MVC Controller mit Command Processing
│   ├── model/
│   │   └── game_model.py         # Neo4j Datenbankoperationen
│   ├── view/
│   │   └── game_view.py          # Rich Terminal UI
│   ├── utils/
│   │   └── command_parser.py     # Text Command Parser
│   └── main.py                   # Entry Point
├── notebooks/
│   ├── 01-neo4j_dbsetup.ipynb    # DB Schema & Spielwelt Setup
│   ├── 02-neo4j_commands.ipynb   # Command Testing
│   └── 03-smart-parser.ipynb     # NLP Parser mit spaCy + Sentence Transformers
├── data/
├── docs/
└── .env                          # Neo4j Credentials (nicht committen!)
```

## 🎮 Spiel starten

```bash
# Virtual Environment aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Spiel starten
python src/main.py
```

## 🗣️ Natürliche Sprache mit dem Smart Parser

Das Spiel versteht **natürliche deutsche Sätze** - du musst keine exakten Befehle kennen!

### Beispiele für Bewegung (go):
```
geh zur Taverne
lauf zum Marktplatz
besuche die Schmiede
renn in den Finsterwald
spaziere zum Brunnen
```

### Beispiele für Items aufnehmen (take):
```
nimm den Schlüssel
hol die Fackel
greif nach dem Hammer
schnapp dir den goldenen Esel
sammel die Streichhölzer auf
pack das Schwert ein
```

### Beispiele für Items ablegen (drop):
```
leg den Schlüssel ab
wirf die Fackel weg
stell den Hammer hin
lass den Beutel fallen
platziere das Schwert
```

### System-Befehle:
- `quit` - Spiel beenden (hart-codiert, kein Parser)

### 🎯 Wie der Parser funktioniert:

Der **Smart Parser** nutzt spaCy und Sentence Embeddings um:
1. **Verben zu extrahieren** (z.B. "schnapp" aus "schnapp dir den Kristall")
2. **Commands zu matchen** via Similarity (77%+ Accuracy)
3. **Objekte zu finden** (aktuell: Nomen im Satz, zukünftig: DB-Matching)

**Aktuell implementierte Commands:**
- `go` - Bewegung (80+ Verben: gehen, laufen, rennen, marschieren, wandern, ...)
- `take` - Aufnehmen (70+ Verben: nehmen, holen, packen, greifen, schnappen, ...)
- `drop` - Ablegen (40+ Verben: ablegen, wegwerfen, hinlegen, fallenlassen, ...)

**Geplante Commands** (Parser vorbereitet, Game-Logik fehlt noch):
- `use` - Benutzen (öffnen, anzünden, kombinieren)
- `examine` - Untersuchen (detaillierte Beschreibungen)
- `read` - Lesen (Bücher, Inschriften)
- `talk` - Sprechen (mit NPCs)
- `look` - Umschauen (Raum untersuchen)

**Vollständige Command-Liste und Verb-Mappings:** siehe `docs/commands.md`

### 🖥️ Das Multi-Panel UI

Das Spiel zeigt alle wichtigen Infos **gleichzeitig** an:

```
┌─────────────────────────────┬─────────────┐
│ Location: Marktplatz        │ Inventar:   │
│ Beschreibung...             │ • Fackel    │
├─────────────────────────────┤ • Schlüssel │
│ Items:                      │             │
│ • Goldener Esel             │             │
│ • Beutel mit Goldmünzen     │             │
├─────────────────────────────┤             │
│ Exits:                      │             │
│ • Taverne                   │             │
│ • Schmiede                  │             │
└─────────────────────────────┴─────────────┘

✓ Schlüssel aufgenommen

What? > _
```

**Features:**
- **Location-Panel:** Name, Beschreibung (immer sichtbar)
- **Items-Panel:** Gegenstände am aktuellen Ort (Live-Update)
- **Exits-Panel:** Erreichbare Orte (Live-Update)
- **Inventory-Panel:** Dein Inventar (Live-Update)
- **Status-Zeile:** Feedback zu Aktionen (temporär)

---


## 🗺️ Roadmap - Plus Extrafeaturs :D

### Phase 1: MVP Foundation ✅ ABGESCHLOSSEN
**Lernziele:** Game Development Fundamentals, MVC-Architektur, Graph-Datenbanken, TUI-Entwicklung

- [x] Neo4j Docker-Container aufsetzen
- [x] Schema-Design implementieren (Location, Item, NPC, Player Nodes)
- [x] Constraints & Indexes erstellen
- [x] Spielwelt aufbauen (4 Locations, 8 Items, 3 NPCs)
- [x] Relationships definieren (IST_IN, ERREICHT, TRÄGT)
- [x] Basis-Datenbankoperationen in Python
- [x] MVC-Architektur aufgebaut (Model, View, Controller)
- [x] Parser: Grundstruktur + Command-Verarbeitung
- [x] Rich UI Basis mit Welcome Screen
- [x] Spieler-Bewegung zwischen Räumen
- [x] Items aufnehmen/ablegen funktioniert
- [x] Embeddings für alle Entities (SentenceTransformers)

**Skills:** MVC Pattern, Game Loop Design, Neo4j Graph-Modellierung, Docker, Rich Library, State Management

**Milestone**: ✅ Funktionierendes Text-Adventure mit Bewegung und Item-Interaktion

---

### Phase 1.5: Smart Parser 🚧 IN ARBEIT
**Lernziele:** Natural Language Processing, spaCy, Embeddings, Semantic Matching

- [x] spaCy Integration (de_dep_news_trf)
- [x] SentenceTransformer Setup (paraphrase-multilingual-MiniLM-L12-v2)
- [x] Verb-Extraktion & Dependency Parsing
- [x] Command-Matching mit Embeddings (6 Commands: take, drop, go, examine, read, use)
- [x] Test-Suite mit 40+ Sätzen (basic, trennbar, komplex, präpositionen, synonyme, schwierig, edge cases)
- [x] Accuracy-Analyse (~77% durchschnittlich)
- [ ] **OFFEN: Object-Matching mit DB-Embeddings** (aktuell nur Verb→Command)
- [ ] **OFFEN: Fuzzy-Matching für Entity-Namen**
- [ ] **OFFEN: Integration in game_controller.py**
- [ ] **OFFEN: Item-Relationship-Design vereinfachen** (aktuell zu spezifisch: KANN_ANZÜNDEN, etc.)

**Offene Architektur-Fragen:**
- Wie generisch sollen Item-Relationships sein? (NUTZBAR_MIT vs. KANN_ANZÜNDEN)
- Object-Matching: Nur Embeddings oder auch Rules?
- Parser-Output-Format für Controller

**Skills:** spaCy NLP, Sentence Embeddings, Semantic Similarity, Dependency Parsing, Test-Driven Development

**Milestone**: Parser versteht natürliche deutsche Sätze und mappt zu Commands

---

### Phase 2: Core Mechanics (verschoben)
**Lernziele:** Relationship-Modellierung, Command Pattern, Data Loading, UI/UX Design

- [ ] NPC-Dialoge (statischer Text aus DB)
- [ ] Quest-System (Relationships & State-Tracking)
- [ ] Story-Konzept ausarbeiten
- [ ] UI: Farbcodierung und alle Panels erweitern
- [ ] Story-Loader: JSON → Neo4j (optional)

**Skills:** Graph Relationships, Command Parser Design, JSON Data Loading, Cypher Queries, Rich Advanced Features

**Milestone**: Interaktive NPCs und Quest-System

---

### Phase 3: LLM Narrator & NPCs
**Lernziele:** LLM Integration, Prompt Engineering, Context Management, AI Personas

- [ ] Ollama Setup (llama3, mistral, qwen)
- [ ] LLM-Service Klasse mit streaming support
- [ ] **Dynamischer Narrator**: Raumbeschreibungen generieren aus GraphDB-Daten
- [ ] **NPC-Persönlichkeiten**: Individuelle System-Prompts pro Charakter
- [ ] **Kontextbewusstsein**: NPCs erinnern sich an vorherige Gespräche
- [ ] **Stimmungs-System**: NPCs reagieren auf Spieler-Aktionen
- [ ] **Emergent Storytelling**: Unvorhersehbare Dialoge & Situationen

**Skills:** Ollama API, System Prompts, Streaming Responses, Conversation History, Prompt Templates, Character Design

**Milestone**: NPCs fühlen sich lebendig an

---

### Phase 4: Advanced Parser Features (teilweise in Phase 1.5)
**Lernziele:** Advanced NLP, Disambiguation, Complex Commands

- [x] Embeddings-basierte Intent-Erkennung (bereits in Phase 1.5)
- [x] Synonym-Handling (bereits in Phase 1.5)
- [ ] Fuzzy-Matching für Objekt/NPC-Namen
- [ ] **LLM-Parser**: Komplexe Mehrfach-Befehle verstehen ("nimm X und gib Y")
- [ ] **MCP Integration evaluieren**: Parser als Model Context Protocol
- [ ] Disambiguation: "Welchen Schlüssel meinst du?" bei Mehrdeutigkeit

**Skills:** Semantic Search, Vector Embeddings, Intent Classification, Model Context Protocol, Fuzzy String Matching

**Milestone**: Parser versteht komplexe Multi-Befehle

---

### Phase 5: Infrastructure Upgrade
**Lernziele:** Advanced Software Architecture, Service Layer Pattern, Type Safety, UI/UX Advanced

**LangChain/LangGraph Migration:**
- [ ] LangChain Service-Layer aufbauen
- [ ] Bestehende LLM-Calls auf LangChain migrieren
- [ ] LangGraph für komplexe Flows evaluieren
- [ ] Chain-Templates & Prompt-Management
- [ ] Memory & Context-Management mit LangChain

**TUI Advanced:**
- [ ] ASCII Art System (statische Files + später LLM-generiert)
- [ ] Advanced Layouts (Multi-Panel, Split-Screens, Live-Updates)
- [ ] Animationen (Typing-Effekt, Fade-Ins, Transitions)
- [ ] Textual Library evaluieren (falls Rich Grenzen erreicht)
- [ ] Custom Themes & Color-Schemes

**Code Quality & Validation:**
- [ ] Pydantic Models für alle Daten-Strukturen
- [ ] Input-Validierung (Commands, User-Input)
- [ ] Neo4j Response-Validierung
- [ ] LLM Output-Validierung (structured output)
- [ ] Error-Handling durchgängig verbessern

**Skills:** LangChain Architecture, Pydantic Validation, Advanced Rich/Textual, Code Refactoring, Error Handling Patterns

**Milestone**: Solide Foundation für komplexe AI-Features

---

### Phase 6: Advanced AI Features
**Lernziele:** Multi-Agent Systems, RAG Architecture, Vector Databases, Procedural Generation

**RAG & Memory:**
- [ ] RAG für NPC-Weltwissen (Lore, Geschichte, Gerüchte)
- [ ] Vector-DB Integration (ChromaDB/Weaviate)
- [ ] Langzeit-Gedächtnis für NPCs über Sessions
- [ ] Dynamisches Lore-Building (NPCs erfinden konsistente Geschichten)

**Procedural Content:**
- [ ] **AI Story-Generator**: Neue Quests aus Templates
- [ ] **Dynamische Items**: LLM generiert Item-Beschreibungen
- [ ] **Prozedurale Räume**: Dungeons on-the-fly generieren
- [ ] **Quest-Variationen**: Gleiche Quest, unterschiedliche Narrative

**Multi-Agent Systems:**
- [ ] **NPC-NPC Interaktionen**: NPCs reden miteinander
- [ ] **Faction-Dynamics**: Gruppen mit eigenen Zielen
- [ ] **AI Dungeon Master**: Meta-Agent orchestriert Story-Bögen
- [ ] **Adaptive Difficulty**: LLM passt Herausforderungen an

**Skills:** RAG Implementation, ChromaDB/Weaviate, LangGraph State Machines, Agent Orchestration, Procedural Content Gen

---

### Phase 7: Analytics & Meta-Features
**Lernziele:** Data Engineering, Analytics, Metrics & Monitoring, A/B Testing

- [ ] Event-Logging (DuckDB) für Player-Behaviour
- [ ] Sentiment-Analyse von Spieler-Eingaben
- [ ] Story-Branching Visualisierung
- [ ] A/B Testing verschiedener Prompts
- [ ] Streamlit Dashboard für NPC-Performance
- [ ] Player-Journey Analytics
- [ ] LLM Cost-Tracking & Optimierung

**Skills:** DuckDB, Event-Driven Architecture, Streamlit Dashboards, Sentiment Analysis, Data Visualization, Cost Optimization

---

### Phase 8: Experimentelle Features
**Lernziele:** Emerging AI Technologies, Multi-Modal AI, Real-Time Systems, Fine-Tuning

- [ ] **Voice-to-Text**: Speak to NPCs
- [ ] **Multi-Modal**: DALL-E/Stable Diffusion für Raum-Visuals
- [ ] **Multiplayer**: Geteilte Welt mit mehreren Spielern
- [ ] **LLM-Training**: Fine-tuning auf eigene Stories
- [ ] **Real-Time World**: Welt verändert sich während Offline
- [ ] **Moralisches Alignment-System**: NPCs beurteilen Spieler-Entscheidungen
- [ ] **Meta-Narration**: 4th-wall-breaking Erzähler

**Skills:** Whisper/Speech-to-Text, DALL-E/SD APIs, WebSockets, Model Fine-Tuning, Distributed Systems, Reinforcement Learning

---

### Laufende Aufgaben (parallel)

- Testing nach jedem Feature
- Dokumentation aktuell halten
- Code-Reviews
- Bug-Tracking

---

## 🎯 Aktueller Stand & Nächste Schritte

**Aktueller Branch:** `smart-parser`

**Was funktioniert:**
- ✅ MVC-Architektur mit Neo4j Backend
- ✅ Spieler-Bewegung, Item-Interaktion
- ✅ Embeddings für alle Entities in DB
- ✅ Smart Parser (Verb→Command mit 77% Accuracy)
- ✅ Umfangreiche Test-Suite für Parser

**In Arbeit:**
- 🚧 Object-Matching mit DB-Embeddings
- 🚧 Integration Smart Parser in Game Controller
- 🚧 Item-Relationship-Design überarbeiten

**Nächste TODOs:**
1. Item-Relationships vereinfachen (zu spezifisch: KANN_ANZÜNDEN → generischer)
2. Object-Matching implementieren (spaCy Objects → DB Entity Embeddings)
3. Parser in Controller integrieren
4. Fackel-Quest funktionsfähig machen (anzünden, Finsterwald beleuchten)
5. README weiter aktualisieren mit aktuellen Architektur-Entscheidungen

**Offene Architektur-Fragen:**
- Item-Relationships: Wie generisch? (NUTZBAR_MIT vs. spezifische Actions)
- Object-Matching: Nur Embeddings oder Hybrid mit Rules?
- State-Management für Items (is_lit, etc.) - Properties vs. Relationships?

---

**Version:** v0.5 (Smart Parser Development)
**Letzte Aktualisierung:** 30. November 2025
**Status:** In Entwicklung 🚧
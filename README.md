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
```

**`requirements.txt`:**
```
rich>=13.0.0
neo4j>=5.0.0
python-dotenv>=1.0.0
jupyter>=1.0.0
```

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
- Generiert die Basis-Spielwelt (3 Locations, NPCs, Items)
- Verknüpft alles mit Relationships

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
│   └── 02-neo4j_commands.ipynb   # Command Testing
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

**Verfügbare Befehle:**
- `show location` - Zeigt aktuellen Ort
- `show directions` - Zeigt erreichbare Orte
- `show inventory` - Zeigt Inventar
- `quit` - Spiel beenden

---


## 🗺️ Roadmap - Plus Extrafeaturs :D

### Phase 1: MVP Foundation (Woche 1)
**Lernziele:** Game Development Fundamentals, MVC-Architektur, Graph-Datenbanken, TUI-Entwicklung

- [x] Neo4j Docker-Container aufsetzen
- [x] Schema-Design implementieren (Location, Item, NPC, Player Nodes)
- [x] Constraints & Indexes erstellen
- [x] Basis-Spielwelt aufbauen (3 Locations, Items, NPCs)
- [x] Relationships definieren (IST_IN, ERREICHT)
- [x] Basis-Datenbankoperationen in Python (create, read für Räume und Player)
- [x] MVC-Architektur aufgebaut (Model, View, Controller)
- [x] Parser: Grundstruktur + Command-Verarbeitung
- [x] Rich UI Basis mit Welcome Screen
- [x] Neo4j Warnings unterdrückt (notifications_min_severity='OFF')
- [X] Spieler-Bewegung zwischen Räumen implementieren
- [X] Items aufnehmen/ablegen funktioniert
- [ ] Story-Konzept ausarbeiten

**Skills:** MVC Pattern, Game Loop Design, Neo4j Graph-Modellierung, Docker, Rich Library, State Management

**Milestone**: Spieler kann sich im Terminal zwischen Räumen bewegen

---

### Phase 2: Core Mechanics (Woche 2)
**Lernziele:** Relationship-Modellierung, Command Pattern, Data Loading, UI/UX Design

- [ ] Item-System in DB (CONTAINS, CARRIES Relationships)
- [ ] Item aufnehmen/ablegen funktioniert
- [ ] NPC-Dialoge (statischer Text aus DB)
- [ ] Quest-System (WANTS/GIVES Relationships)
- [ ] Parser: Alle Befehle (take, talk, look, inventory, help, quit)
- [ ] Story-Loader: JSON → Neo4j
- [ ] Komplette Story-Datei schreiben (Räume, Items, NPCs, Dialoge)
- [ ] UI: Farbcodierung und alle Panels

**Skills:** Graph Relationships, Command Parser Design, JSON Data Loading, Cypher Queries, Rich Advanced Features

**Milestone**: Alle Einzelkomponenten funktionieren isoliert

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

### Phase 4: Intelligent Parser & Understanding
**Lernziele:** Natural Language Processing, Embeddings, Intent Recognition, MCP Architecture

- [ ] **Natural Language Commands**: "Gib dem Wächter das Schwert" statt Keyword-Matching
- [ ] Embeddings-basierte Intent-Erkennung (sentence-transformers)
- [ ] Fuzzy-Matching für Objekt/NPC-Namen
- [ ] **LLM-Parser**: Komplexe Mehrfach-Befehle verstehen
- [ ] **MCP Integration evaluieren**: Parser als Model Context Protocol
- [ ] Disambiguation: "Welchen Schlüssel meinst du?" bei Mehrdeutigkeit
- [ ] Synonym-Handling (gehen/laufen/rennen)

**Skills:** Semantic Search, Vector Embeddings, Intent Classification, Model Context Protocol, Fuzzy String Matching

**Milestone**: Spiel versteht natürliche Sprache

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

**Version:** MVP v1.0  
**Letzte Aktualisierung:** November 2025  
**Status:** In Entwicklung 🚧
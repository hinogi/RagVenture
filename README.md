# AI-Textadventure - Setup & Installation

Ein textbasiertes Adventure-Game mit Neo4j GraphDB und Rich Terminal UI.

**Timeline:** 4 Wochen MVP, dann AI-Integration in v2  
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

---

## 🗂️ Projektstruktur

```
textadventure/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── views/
│   └── utils/
├── data/
├── notebooks/
├── docs/
```

---


## 🗺️ Roadmap

### Phase 1: MVP Foundation (Woche 1)

- [ ] Neo4j Docker-Container aufsetzen
- [ ] Schema-Design implementieren (Room, Item, NPC, Player Nodes)
- [ ] Basis-Datenbankoperationen (create, read für Räume und Player)
- [ ] Spieler-Bewegung zwischen 2 Räumen funktioniert
- [ ] Rich UI Prototyp mit 3-Panel-Layout
- [ ] Parser: Grundstruktur + Bewegungsbefehle
- [ ] Story-Konzept ausarbeiten

**Milestone**: Spieler kann sich im Terminal zwischen Räumen bewegen

---

### Phase 2: Core Mechanics (Woche 2)

- [ ] Item-System in DB (CONTAINS, CARRIES Relationships)
- [ ] Item aufnehmen/ablegen funktioniert
- [ ] NPC-Dialoge (statischer Text aus DB)
- [ ] Quest-System (WANTS/GIVES Relationships)
- [ ] Parser: Alle Befehle (take, talk, look, inventory, help, quit)
- [ ] Story-Loader: JSON → Neo4j
- [ ] Komplette Story-Datei schreiben (Räume, Items, NPCs, Dialoge)
- [ ] UI: Farbcodierung und alle Panels

**Milestone**: Alle Einzelkomponenten funktionieren isoliert

---

### Phase 3: LLM Narrator & NPCs

- [ ] Ollama Setup (llama3, mistral, qwen)
- [ ] LLM-Service Klasse mit streaming support
- [ ] **Dynamischer Narrator**: Raumbeschreibungen generieren aus GraphDB-Daten
- [ ] **NPC-Persönlichkeiten**: Individuelle System-Prompts pro Charakter
- [ ] **Kontextbewusstsein**: NPCs erinnern sich an vorherige Gespräche
- [ ] **Stimmungs-System**: NPCs reagieren auf Spieler-Aktionen
- [ ] **Emergent Storytelling**: Unvorhersehbare Dialoge & Situationen

**Milestone**: NPCs fühlen sich lebendig an

---

### Phase 4: Intelligent Parser & Understanding

- [ ] **Natural Language Commands**: "Gib dem Wächter das Schwert" statt Keyword-Matching
- [ ] Embeddings-basierte Intent-Erkennung (sentence-transformers)
- [ ] Fuzzy-Matching für Objekt/NPC-Namen
- [ ] **LLM-Parser**: Komplexe Mehrfach-Befehle verstehen
- [ ] Disambiguation: "Welchen Schlüssel meinst du?" bei Mehrdeutigkeit
- [ ] Synonym-Handling (gehen/laufen/rennen)

**Milestone**: Spiel versteht natürliche Sprache

---

### Phase 5: Advanced AI Features

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

---

### Phase 6: Analytics & Meta-Features

- [ ] Event-Logging (DuckDB) für Player-Behaviour
- [ ] Sentiment-Analyse von Spieler-Eingaben
- [ ] Story-Branching Visualisierung
- [ ] A/B Testing verschiedener Prompts
- [ ] Streamlit Dashboard für NPC-Performance
- [ ] Player-Journey Analytics
- [ ] LLM Cost-Tracking & Optimierung

---

### Phase 7: Experimentelle Features

- [ ] **Voice-to-Text**: Speak to NPCs
- [ ] **Multi-Modal**: DALL-E/Stable Diffusion für Raum-Visuals
- [ ] **Multiplayer**: Geteilte Welt mit mehreren Spielern
- [ ] **LLM-Training**: Fine-tuning auf eigene Stories
- [ ] **Real-Time World**: Welt verändert sich während Offline
- [ ] **Moralisches Alignment-System**: NPCs beurteilen Spieler-Entscheidungen
- [ ] **Meta-Narration**: 4th-wall-breaking Erzähler

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
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

### Phase 3: Integration (Woche 3)

- [ ] Game Loop implementieren (State → Render → Input → Parse → Execute)
- [ ] Win-Condition prüfen
- [ ] Alle Komponenten verbinden (main.py)
- [ ] Error-Handling durchgängig
- [ ] Komplette Story durchspielbar
- [ ] Bug-Fixes aus erstem Testing
- [ ] Help-System vollständig

**Milestone**: Story ist von Anfang bis Ende spielbar

---

### Phase 4: Polish (Woche 4)

- [ ] Bug-Fixes (nach Priorität)
- [ ] README.md mit Setup-Anleitung
- [ ] Code-Dokumentation
- [ ] Usability-Verbesserungen (Messages, Feedback)
- [ ] Edge-Cases abdecken
- [ ] requirements.txt finalisieren
- [ ] Finale Tests

**Milestone**: MVP ist auslieferbar

---

### Phase 5: LLM Integration (v2, Wochen 5-8)

- [ ] Ollama Setup und erste Tests
- [ ] Narrator: Dynamische Raumbeschreibungen
- [ ] NPC-Dialoge über LLM statt statischer Text
- [ ] System-Prompts pro NPC
- [ ] Context-Management für Dialoge

---

### Phase 6: Smart Parser (v2, Wochen 9-10)

- [ ] sentence-transformers evaluieren
- [ ] Embeddings-basierter Parser
- [ ] Intent-Klassifikation
- [ ] Natural Language Understanding testen

---

### Phase 7: Advanced Features (v3, nach Bedarf)

- [ ] RAG für NPC-Wissen
- [ ] Story-Generator (LLM erstellt neue Stories)
- [ ] Event-Logging (DuckDB)
- [ ] BI-Dashboard (Streamlit/andere Tools)
- [ ] Save/Load System
- [ ] Weitere Stories

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
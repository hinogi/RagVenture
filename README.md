# RagVenture - NLP Text Adventure

Ein textbasiertes Adventure-Game als **Lernprojekt für NLP, Graph-Datenbanken und Python**.

Entwickelt mit **Claude als Coding-Buddy und "Live-Forum"** - ein Experiment, wie weit man mit natürlicher Sprachverarbeitung, Embeddings und Neo4j in einem klassischen Textadventure kommt.

**Projektziele:**
- Mit **NLP-Techniken** arbeiten (spaCy, Embeddings, später LLMs)
- Verschiedene **ML-Models ausprobieren** und verstehen
- **Python lernen** in praktischer Anwendung
- Neo4j **Graph-Datenbanken** für komplexe Spielwelten nutzen

**Das vermutlich einzige Textadventure mit 1,5GB Speicherbedarf und Online-Zwang.** Willkommen in der Zukunft! 🤖

**Tech-Stack:** Python 3.10+, Neo4j (Docker), Rich Terminal UI, spaCy, SentenceTransformers

---

## 🗂️ Projektstruktur

```
src/
├── controller/game_controller.py  # MVC Controller, State-Machine
├── model/
│   ├── world_model.py             # Neo4j Queries (Cypher)
│   └── game_state.py              # GameState, LoopStatus, Action
├── view/game_view.py              # Rich Terminal UI
├── utils/
│   ├── smart_parser.py            # spaCy NLP Parser
│   └── embedding_utils.py         # Singleton für Embeddings
└── main.py

notebooks/
├── 01-neo4j_dbsetup.ipynb         # Welt-Setup (typsichere Helper)
├── 02-neo4j_commands.ipynb        # Query-Testing
└── 03-smart-parser.ipynb          # Parser-Entwicklung

docs/
├── architecture.md                # Architektur & State-Machine
├── world_schema.md                # Graph-Schema (Nodes, Relationships)
└── commands.md                    # Command-System, Verb-Mappings
```

---

## 🚀 Installation

```bash
# Neo4j Container starten
docker run -d --name textadv-dev -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password neo4j:latest

# Python Environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download de_dep_news_trf

# Config
cp .env.example .env  # Dann NEO4J_URI/USER/PASSWORD eintragen

# Spielwelt initialisieren
jupyter notebook  # → notebooks/01-neo4j_dbsetup.ipynb ausführen

# Spielen!
python src/main.py
```

**Neo4j Browser:** http://localhost:7474 (neo4j / password)

### Docker-Befehle für Neo4j

```bash
# Container-Status prüfen
docker ps | grep neo4j

# Container stoppen/starten
docker stop textadv-dev
docker start textadv-dev

# Logs ansehen (bei Problemen)
docker logs textadv-dev

# Container komplett löschen (Daten weg!)
docker rm textadv-dev
```

---

## 🎮 Das Spiel

### Natürliche Sprache

Das Spiel versteht **natürliche deutsche Sätze** - keine starren Befehle!

**Beispiele:**
```
gehe zur Taverne          # Bewegung
nimm den Schlüssel        # Aufnehmen
lass die Fackel fallen    # Ablegen
```

### Verfügbare Commands

**Aktuell spielbar:**
- `go` - Bewegung zu anderen Orten
- `take` - Items aufnehmen
- `drop` - Items ablegen
- `quit` - Spiel beenden

**Wie es funktioniert:**
1. **Parser (spaCy):** Extrahiert Verb und Objekt aus natürlicher Sprache
2. **Verb-Matching (Embeddings):** "schnapp" → Command "take" via Cosine Similarity
3. **Entity-Matching (Embeddings):** "Taverne" → Location "Mo's Taverne" in Neo4j

Das Spiel versteht **Synonyme** - statt "gehe" kannst du auch "laufe", "renne" oder "besuche" sagen.

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

## 📊 Status

Aktuell läuft ein größeres Refactoring der Architektur. Der Parser und das Embedding-Matching funktionieren gut, jetzt geht's darum, den Game Loop sauber zu strukturieren.

**Was läuft:**
Der Parser holt sich Verben und Objekte zuverlässig aus den Sätzen. Das Verb-zu-Command-Mapping mit dem multilingualen Embedding-Model klappt überraschend gut - besser als die deutschsprachigen Alternativen die ich probiert habe. Entity-Matching funktioniert auch. Neo4j für den Spielzustand ist elegant, Relationships machen das Ganze schön übersichtlich.

**Woran ich gerade arbeite:**
State-Machine für den Game Loop. Statt verschachtelter Handler gibt's jetzt einen klaren Flow: PARSE → VERIFY → REQUEST → ACTION. Das macht den Code lesbarer und einfacher zu erweitern. Dazu gehören typsichere Enums (`LoopStatus`, `ActionCommands`) und Dataclasses (`GameState`, `Action`).

**Bisherige Learnings:**
- Das Model hat Probleme mit Tippfehlern - ist halt nicht darauf trainiert
- Komplizierte Sätze sind schwierig (trainiert auf Nachrichten, nicht Umgangssprache)
- Entity-Matching in Neo4j ging ohne Plugins nicht → läuft jetzt in Python
- Deutschsprachiges Model (`gbert`) funktionierte schlechter als multilingual

**Technisch:**
- MVC-Pattern mit Controller als State-Machine
- Singleton für EmbeddingUtils (1,5GB Model nur einmal laden)
- Embedding-basiertes Matching statt String-Vergleiche
- DB ist Single Source of Truth (kein Caching)
- Typsichere Dataclasses mit Enums

**Ideen für später:**
- **Semantic Search:** Statt nur Cosine Similarity vielleicht top_k mit Clustering oder Cross-Encoder
- **Statechart:** Die State-Machine könnte noch formaler werden (XState-Style)
- **LLM-Integration:** NPCs mit Ollama zum Leben erwecken, Memory-System für Spieler-Aktionen
- **Mehr Commands:** `examine`, `use`, `read`, komplexere Satzstrukturen
- **Graph-Features:** Pathfinding, mehr Item-Eigenschaften

Kein fixer Plan - das entwickelt sich organisch je nachdem worauf ich grad Lust habe und was ich lernen will. :)

---

**Version:** v0.9 (State-Machine Refactoring)
**Letztes Update:** 25. Dezember 2024
**Status:** In aktiver Entwicklung 🚧
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
├── controller/game_controller.py  # MVC Controller, Orchestrierung
├── model/
│   ├── world_model.py             # Neo4j Queries (Cypher)
│   ├── game_state.py              # GameState Container (Statechart-Ready)
│   ├── world_state.py             # WorldState Dataclass
│   └── conversation_state.py      # ConversationState + Status Enum
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
├── world_schema.md                # Graph-Schema (Nodes, Relationships)
├── commands.md                    # Command-System, Verb-Mappings
├── conversation_system.md         # Statechart-Ready Architektur
└── architecture_idea.md           # Architektur-Vision
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

Bin aktuell echt zufrieden mit dem Projekt! Der Parser erkennt die Begriffe ziemlich gut, und das Verb-Matching funktioniert besser als gedacht.

**Was läuft:**
Der Parser holt sich Verben und Objekte zuverlässig aus den Sätzen. Das Verb-zu-Command-Mapping mit dem multilingualen Embedding-Model klappt überraschend gut - besser als die deutschsprachigen Alternativen die ich probiert habe. Entity-Matching funktioniert auch, obwohl ich vom ursprünglichen Plan abweichen musste (dazu gleich mehr). Neo4j für den Spielzustand ist elegant, Relationships machen das Ganze schön übersichtlich.

**Wos hakt:**
Das Model hat Probleme mit falsch geschriebenen Worten - klar, ist halt nicht darauf trainiert. Komplizierte Sätze sind auch noch schwierig, liegt wohl daran dass das Ding auf Nachrichten trainiert ist und nicht auf Umgangssprache. Das wird die weitere Entwicklung vermutlich komplizierter machen wenn ich mehr Satzstrukturen unterstützen will.

**Item-Matching - Plan vs. Realität:**
Eigentlich wollte ich das Entity-Matching direkt in den Neo4j Queries machen. Allerdings geht das ohne Plugins oder so nicht. Aktuell läuft's zweistufig: Parser → Python macht Embedding-Matching → Neo4j holt die Daten. Funktioniert super, kein Problem damit!

**Model-Experimente:**
Zwischendurch hab ich mal ein deutschsprachiges Model probiert (`gbert`) - ging erstaunlicherweise in die Hose. Multilingual ist stabiler. Vielleicht nicht mehr wenn ich das Projekt umbauen würde und die Syntax nicht markieren lassen würde... k.A.

**Technisch:**
- MVC-Pattern mit Controller, Model (Neo4j), View (Rich UI)
- Singleton für EmbeddingUtils damit ich die nicht überall neu laden muss
- Embedding-basiertes Matching statt String-Vergleiche
- Helper-Funktionen in den Notebooks für typsichere Entity-Erstellung

**Was als nächstes kommt:**
* Jetzt muss das Spiel erstmal richtig spielbar machen - bedeutet: Validation und Error Handling einbauen
* Embedding_Utils verbessern, zum Beispiel mit Semantic Search statt Cosine Similarity. Das kann uns top_k zurückgeben und vielicht kann man schauen, in welchem Cluster die meisten Verben passen... Ansonsten würde ich noch einen Cross Encoder ausprobieren, mal sehen was das in dem Fall bringt
* Fürs Game noch ein, zwei Commands mehr (`examine`, `use`, vielleicht `read`). Längere Sätze sollten auch besser funktionieren
* Ich möchte auch noch ein bisschen mehr mit dem Graphen herumspielen und features wie Pathfinding und mehr Eigenschaften der Gegenstände integrieren
* Weiter in der Ferne könnte man NPCs zum Sprechen bringen mit nem LLM (Ollama) und ein Memory-System bauen damit der Spieler sich an seine Aktionen erinnert
* Und generell noch mehr Features in die Welt einbauen 

Hab aber keinen fixen Plan - das entwickelt sich einfach organisch je nachdem worauf ich grad Lust habe und was ich lernen will. :)

---

**Version:** v0.8 (Entity Matching & Command Activation)
**Letztes Update:** 13. Dezember 2024
**Status:** In aktiver Entwicklung 🚧
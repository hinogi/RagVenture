# CLAUDE.md

This file provides quick orientation for Claude Code when starting a new chat session.

## Project Overview

**RagVenture** - German text-based adventure game for learning NLP, Graph-DBs, and Python.

**Tech Stack:** Python 3.10+, Neo4j (Docker), Rich Terminal UI, spaCy (de_dep_news_trf), SentenceTransformers (paraphrase-multilingual-MiniLM-L12-v2)

**Current Phase:** State-Machine refactoring (v0.9) - Building robust game loop with REQUEST handling

## Quick Start

```bash
source venv/bin/activate          # Activate environment
docker start textadv-dev          # Start Neo4j (localhost:7474, neo4j/password)
python src/main.py                # Run game

# Setup (first time):
jupyter notebook                  # Run notebooks/01-neo4j_dbsetup.ipynb
```

## Architecture

### MVC with State-Machine

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Controller  │ ───→ │ WorldModel  │ ───→ │   Neo4j     │
│             │      │  (Queries)  │      │  (Graph DB) │
│    State    │      └─────────────┘      └─────────────┘
│   Machine   │           ↑
└─────────────┘           │
       │                  │
       ↓                  │
┌─────────────┐          │
│    View     │          │
│ (Rich UI)   │ ←────────┘
└─────────────┘
```

**State-Machine Flow:**
```
PARSE → VERIFY → REQUEST → ACTION → (zurück zu PARSE)

PARSE:   User Input → spaCy → verb/noun extrahieren
VERIFY:  verb/noun → Embedding-Matching → command/target finden
REQUEST: Bei Mehrdeutigkeit → Dialog anzeigen → User-Auswahl verarbeiten
ACTION:  Command ausführen → DB update → View refresh
```

**GameState Structure (src/model/game_state.py):**
```python
@dataclass
class Parse:
    input: str | None
    verb: str | None
    noun: str | None
    command_matches: list
    target_matches: list

@dataclass
class Dialog:
    type: DialogState              # MESSAGE, REQUEST_VERB, REQUEST_NOUN
    message: str | None
    choices: list

@dataclass
class Action:
    command: ActionCommands | None # GO, TAKE, DROP
    target: str | None             # Entity ID

@dataclass
class GameState:
    running: bool
    loop_state: LoopStatus         # PARSE, VERIFY, REQUEST, ACTION

    parse: Parse
    dialog: Dialog
    action: Action
```

### Key Patterns

**1. DB is Single Source of Truth**
```python
# ALWAYS load fresh - no caching!
location = self.model.current_location()
items = self.model.location_items()
exits = self.model.location_exits()
```

**2. Atomic View Updates**
```python
# Nach Action: Update nur betroffene Panels
self.view.update_location(location)
self.view.update_items(items)
self.view.update_dialog(dialog)
self.view.refresh()  # Commit alle Änderungen
```

**3. Embedding-Matching**
```python
# Command-Matching (threshold 0.95)
commands = embedding_utils.verb_to_command(verb)
good = [c for c in commands if c['sim'] >= 0.95]

# Entity-Matching (threshold 0.70)
targets = embedding_utils.match_entities(noun, candidates)
good = [t for t in targets if t['score'] >= 0.70]
```

**4. Neo4j Queries**
```python
# Immer parameterisiert!
query = "MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc) RETURN loc"
results = self._run_query(query, params={'id': 'player'})
# Returns: list of dicts
```

### Project Structure

```
src/
├── controller/game_controller.py  # State-Machine, _handle_parse/_choice
├── model/
│   ├── world_model.py             # Neo4j Queries (Cypher)
│   └── game_state.py              # Parse, Dialog, Action Dataclasses
├── view/game_view.py              # Rich UI (atomic updates)
└── utils/
    ├── smart_parser.py            # spaCy (verb/noun extraction)
    └── embedding_utils.py         # SentenceTransformer (Singleton!)

docs/
├── architecture.md                # Detailed architecture docs
├── world_schema.md                # Neo4j schema (Nodes, Relationships)
└── commands.md                    # Command system reference

notebooks/
└── 01-neo4j_dbsetup.ipynb        # World initialization (typsafe helpers)
```

## Git Workflow

**You handle ALL git operations** (add, commit, merge, push, etc.)

**Critical Rules:**
- Always merge with `--no-ff` (no fast-forward)
- Write descriptive commit messages
- Ask if unsure about branch names or commit messages

```bash
# Merge pattern
git checkout master
git merge --no-ff feature-branch -m "Merge branch 'feature-branch' - Description"
```

**Commit Message Format:**
```
feat: Short description

Detailed explanation:
- Bullet point 1
- Bullet point 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Important Context

### Language
- **All text in German**: Comments, docs, user-facing messages
- Variable names: English or German (mixed)
- Neo4j properties: German names

### Neo4j Schema Essentials
- **Nodes:** Player, Location, Item, NPC
- **Key Relationships:** IST_IN (containment), ERREICHT (connections), TRÄGT (inventory), ÖFFNET (unlocks)
- **IDs:** Always lowercase, no spaces (e.g., `taverne`, `schluessel`)
- **Player ID:** Always `'player'`
- **Full schema:** `docs/world_schema.md`

### Commands (Current)
- `go <location>` - Bewegung (versteht: gehen, laufen, rennen, ...)
- `take <item>` - Aufnehmen (versteht: nehmen, holen, packen, ...)
- `drop <item>` - Ablegen (versteht: ablegen, wegwerfen, ...)
- `quit` - Beenden

### Common Gotchas
1. **Check list bounds!** `match_entities()` kann `[]` zurückgeben
2. **Parser returns list:** `parsed[0]['verb']` nicht `parsed['verb']`
3. **Dataclass access:** `self.state.parse.verb` nicht `self.state['parse']['verb']`
4. **Enum comparisons:** `self.state.loop_state == LoopStatus.PARSE`
5. **Neo4j directions matter:** `(a)-[:REL]->(b)` ≠ `(a)<-[:REL]-(b)`
6. **EmbeddingUtils is Singleton** (1.5GB model - load once!)

## Documentation

**Read when needed:**
- `docs/architecture.md` - Detailed architecture & patterns
- `docs/world_schema.md` - Complete Neo4j schema
- `docs/commands.md` - Full command reference
- `README.md` - Setup & project status

**Quick reference always in:** This file (CLAUDE.md)
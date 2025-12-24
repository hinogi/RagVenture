# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RagVenture is a German-language text-based adventure game using Neo4j graph database for world state, Rich library for terminal UI, and following MVC architecture. The project is in Phase 1 (MVP Foundation) with plans to integrate LLM-based narration and NPCs in later phases.

**Tech Stack:** Python 3.10+, Neo4j (Docker), Rich Terminal UI, spaCy (de_dep_news_trf), SentenceTransformers (paraphrase-multilingual-MiniLM-L12-v2), (future: Ollama for LLM integration)

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Neo4j Database
```bash
# Check if Neo4j container is running
docker ps | grep neo4j

# Start existing container (if stopped)
docker start textadv-dev

# Access Neo4j Browser
# URL: http://localhost:7474
# Credentials: neo4j / password (from .env)

# Reset database (WARNING: deletes all data)
# Run in Neo4j Browser: MATCH (n) DETACH DELETE n
# Then re-run notebooks/01-neo4j_dbsetup.ipynb
```

### Initialize World Data
```bash
# Start Jupyter and run setup notebook
jupyter notebook
# Open and execute: notebooks/01-neo4j_dbsetup.ipynb
# This creates:
# - Schema constraints (unique IDs)
# - Vector indexes (for Smart Parser)
# - Locations, Items, NPCs, Player
# - Relationships (connections, placements, interactions)

# Das Notebook nutzt Helper-Funktionen für typsichere Erstellung:
# - create_item(), create_location(), create_npc(), create_player()
# - connect_locations(), place_item(), make_key_unlock(), etc.
# - Verhindert Tippfehler bei Relationship-Names
```

### Run Game
```bash
python src/main.py
```

### Debug Database State
```bash
# Use the debug script to inspect current game state
python debug_db.py
```

## Architecture

### Statechart-Ready MVC Pattern

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Controller  │ ───→ │ Repository  │ ───→ │  Database   │
│             │      │ (WorldModel)│      │   (Neo4j)   │
│    ↓        │      └─────────────┘      └─────────────┘
│  State      │           │
│ (GameState) │ ←─────────┘
└─────────────┘
```

**Komponenten:**
- **Repository** (`src/model/world_model.py`): Neo4j Queries, gibt Daten zurück
- **View** (`src/view/game_view.py`): Rich terminal UI
- **Controller** (`src/controller/game_controller.py`): Orchestriert alles
- **State** (Dataclasses mit Methoden):
  - `src/model/game_state.py`: `GameState` - Container für alle States
  - `src/model/world_state.py`: `WorldState` - location, items, exits, inventory
  - `src/model/conversation_state.py`: `ConversationState` - status, question, options
- **Utils** (Pure Functions):
  - `src/utils/smart_parser.py`: `SmartParserUtils`
  - `src/utils/embedding_utils.py`: `EmbeddingUtils`

**Architektur-Prinzipien:**
1. **Controller orchestriert** - holt Daten von Repository, speichert in State
2. **Dataclasses mit Methoden** - kapseln ihre eigene Logik (z.B. `state.conversation.ask()`)
3. **Utils sind pure** - Input → Output, keine Side Effects
4. **Ein State-Container** - `GameState` enthält `WorldState` + `ConversationState` (Statechart-ready)

### Key Design Decisions

**Neo4j Graph Schema:**
- Nodes: `Player`, `Location`, `Item`, `NPC`
- Relationships (vollständige Liste in `docs/world_schema.md`):
  - `IST_IN` - location/containment (Item/NPC/Player → Location)
  - `ERREICHT` - location connections (bidirektional)
  - `TRÄGT` - player/NPC inventory
  - `ÖFFNET` - item unlocks item/location (Schlüssel → Truhe)
  - `KANN_ANZÜNDEN` - item lights item (Streichhölzer → Fackel)
  - `BELEUCHTET` - item illuminates location (Fackel → Finsterwald)
  - `KANN_BRECHEN` - item breaks item (Hammer → Truhe)
- All IDs use lowercase, no spaces (e.g., `schluessel`, `taverne`)
- Player node always has ID `'player'`
- **WICHTIG:** Nur definierte Relationship-Types nutzen! (siehe `docs/world_schema.md`)

**Cypher Query Patterns:**
- Always use parameterized queries: `self._run_query(query, params={'key': value})`
- Model methods return lists of dicts from Neo4j results
- Use proper relationship directions: `(a)-[:REL]->(b)` matters
- Filter by node labels in WHERE when needed: `WHERE 'Item' IN labels(entity)`

**Entity Embeddings in Neo4j:**
- Jedes Entity (Location, Item, NPC) hat eine `name_emb` Property
- `name_emb` ist ein Float-Array (384 Dimensionen) vom SentenceTransformer
- Wird beim Setup im Notebook generiert: `model.encode(name + " " + description)`
- **WICHTIG:** Embeddings können NICHT in Neo4j gespeichert werden (kein Array-Type!)
- **Workaround:** Embeddings werden im Notebook erstellt und bleiben in `game_state` (in-memory)
- Entity-Matching passiert in Python, nicht in Cypher
- Bei neuen Entities: Embedding in Notebook generieren und zu `name_emb` Property hinzufügen

**Command Processing Flow:**
```
User Input
  → SmartParser (spaCy) → extracts verb + noun
  → EmbeddingUtils.verb_to_command() → semantic matching (cosine similarity)
  → Controller validates (threshold 0.95)
  → EmbeddingUtils.match_entities() → finds target in game_state
  → Model executes Cypher query
  → Controller updates game_state
  → View displays result
```

**Parser Output Format (SmartParser.parse()):**
```python
[{
    'verb': str | None,     # Lemmatized verb (e.g., "gehen" from "gehe")
    'noun': str | None,     # First noun found (e.g., "Taverne")
    'adjects': None,        # Reserved for future use
    'raw': str              # Original input
}]
```

**Embedding Matching Output:**
```python
# verb_to_command() returns:
[
    {'command': 'go', 'sim': 0.9999},
    {'command': 'take', 'sim': 0.8708},
    ...
]  # Sorted by similarity, descending

# match_entities() returns:
[
    {'id': 'taverne', 'name': "Mo's Taverne", 'score': tensor(0.95)},
    {'id': 'wald', 'name': 'Finsterwald', 'score': tensor(0.42)},
    ...
]  # Sorted by score, descending
```

### Current Game Commands

**Aktuell implementiert (mit Smart Parser):**
- `go <location>` - Bewegen (versteht: gehen, laufen, rennen, besuchen, marschieren, wandern, etc.)
- `take <item>` - Aufnehmen (versteht: nehmen, holen, packen, greifen, schnappen, etc.)
- `drop <item>` - Ablegen (versteht: ablegen, wegwerfen, hinlegen, fallenlassen, etc.)
- `quit` - Beenden (hardcoded, kein Parser)

**Geplante Commands (Parser vorbereitet, Game-Logik fehlt):**
- `use <item> [on <target>]` - Item benutzen/kombinieren
- `examine <object>` - Detailliert untersuchen
- `read <item>` - Lesbares lesen
- `talk [to] <npc>` - Mit NPC sprechen
- `look` - Umgebung betrachten

**Command-Validierung:**
- Threshold für Verb-Matching: **0.95** (nur Commands mit >95% Similarity werden akzeptiert)
- Bei mehrdeutigen Verben (>1 Match über Threshold): Rückfrage geplant (noch nicht implementiert)
- Bei keinem Match: "Was möchtest du tun?"

**Vollständige Command-Referenz:** `docs/commands.md`

## Git Workflow

**Branch Strategy:**
- `master` - main branch
- Feature branches for new functionality (e.g., `world-interactions`, `model`)
- **Always use `--no-ff` when merging** to preserve branch structure in git graph

```bash
# Merge with visible branch structure
git checkout master
git merge --no-ff feature-branch -m "Merge branch 'feature-branch' - Description"
```

**Commit Message Format:**
```
feat: Short description

Detailed explanation of changes:
- Bullet point 1
- Bullet point 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Important Context

### Language
- All code comments, documentation, and user-facing text are in **German**
- Variable names may be in English or German
- Neo4j property names are in German

### Database Connection
- Connection params come from `.env` file (not committed)
- Neo4j container name: `textadv-dev`
- Ports: 7474 (HTTP), 7687 (Bolt)
- Use `notifications_min_severity='OFF'` in driver config (optional, currently commented out)

### Logging & Debugging
- **Log-Datei:** `parser_debug.log` (im Projektroot, nicht committed)
- **Log-Level:** INFO
- **Was wird geloggt:**
  - Parser Input/Output (Verb/Noun Extraktion)
  - Embedding Matches mit Similarity-Scores
  - Game State Updates
- **Debugging-Tipps:**
  - Bei Parser-Problemen: `tail -f parser_debug.log` während des Spielens
  - Neo4j Browser: http://localhost:7474 für manuelle Queries
  - `debug_db.py` für Spielzustand-Inspektion
- **Wichtig:** `logging.basicConfig()` wird in mehreren Modulen aufgerufen (smart_parser, embedding_utils) - kann zu Konflikten führen, sollte zentralisiert werden

### Common Patterns

**Adding a new Model method with Neo4j query:**
```python
def method_name(self, param):
    query = """
    MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
    MATCH (entity)-[:RELATIONSHIP]->(target)
    WHERE conditions
    RETURN entity.property
    """
    params = {'param': param}
    return self._run_query(query, params=params)
```

**Adding a new Controller command with Smart Parser:**
```python
# After verb/noun validation in process_input()
elif best_command == 'new_command':
    if not noun:
        return "Was genau?"
    else:
        # Match entity from game_state
        matches = self.embedding_utils.match_entities(
            noun,
            self.game_state['items']  # or 'exits', 'inventory', etc.
        )

        # Always check if matches found!
        if not matches:
            return f"Ich kann '{noun}' nicht finden."

        # Execute command
        result = self.model.new_command_method(matches[0]['id'])

        if result:
            return f"Erfolgsmeldung: {result[0]['name']}"
        else:
            return "Fehlermeldung"
```

**EmbeddingUtils Singleton Pattern:**
```python
# Automatisches Singleton - jeder Aufruf gibt gleiche Instanz zurück
embedding_utils = EmbeddingUtils()  # Lädt Model beim ersten Mal
embedding_utils2 = EmbeddingUtils() # Gibt gleiche Instanz zurück

# Wichtig: Verhindert mehrfaches Laden des 1.5GB Models!
# Model wird nur einmal in _instance gespeichert
```

**Game Loop Pattern (Controller orchestriert):**
```python
def run_game(self):
    self._run_game(True)  # game_state.running = True
    self.view.show_welcome()

    while self.game_state.running:
        # 1. State aktualisieren & rendern
        self._update_game_state()
        self.view.refresh()

        # 2. Input holen
        user_input = self.view.get_input()

        if user_input == 'quit':
            self.game_state.running = False
            break

        # 3. Parsing
        parsed = self.parser_utils.parse(user_input)
        verb, noun = parsed[0]['verb'], parsed[0]['noun']

        # 4. Command-Matching
        commands = self.embedding_utils.verb_to_command(verb)
        good_commands = [c for c in commands if c['sim'] >= 0.95]

        # 5. Command ausführen
        # ...
```

**State Dataclasses (mit Methoden):**
```python
# model/game_state.py
@dataclass
class GameState:
    running: bool = False
    world: WorldState = field(default_factory=WorldState)
    conversation: ConversationState = field(default_factory=ConversationState)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

# model/world_state.py
@dataclass
class WorldState:
    location: dict | None = None
    items: list = field(default_factory=list)
    exits: list = field(default_factory=list)
    inventory: list = field(default_factory=list)

    def update(self, location, items, exits, inventory):
        self.location = location
        self.items = items
        self.exits = exits
        self.inventory = inventory

# model/conversation_state.py
class Status(Enum):
    PROMPT = 'wait_for_prompt'
    REQUEST = 'wait_for_choice'

@dataclass
class ConversationState:
    status: Status = Status.PROMPT
    question: str | None = None
    options: list = field(default_factory=list)
    message: str | None = None

    def ask(self, question: str, options: list):
        self.status = Status.REQUEST
        self.question = question
        self.options = options

    def reset(self):
        self.status = Status.PROMPT
        self.question = None
        self.options = []

    def is_waiting(self) -> bool:
        return self.status == Status.REQUEST
```

**Zugriff im Controller:**
```python
self.state = GameState()
self.state.start()
self.state.world.update(loc, items, exits, inv)
self.state.conversation.ask("Wohin?", options)
if self.state.conversation.is_waiting():
    ...
```

### Known Gotchas

1. **CRITICAL: Always check list bounds** - `match_entities()` kann leere Liste zurückgeben! IMMER prüfen: `if not matches: return error`
2. **verb_to_command() returns list** - Nicht `command['best_command']` sondern `command[0]['command']` nach Filtern
3. **Parser returns list of dicts** - `parsed[0]['verb']` nicht `parsed['verb']`
4. **GameState ist Dataclass** - Zugriff via `self.state.running`, nicht `self.state['running']`
5. **ConversationState.status ist Enum** - Vergleiche mit `Status.PROMPT`, `Status.REQUEST`
6. **Prompt-Wechsel bei Rückfragen** - Bei `self.state.conversation.is_waiting()` Prompt ändern
7. **Python dict vs set syntax** - `{'key': value}` not `{'key', value}`
8. **Relationship directions matter** - `(a)-[:REL]->(b)` is different from `(a)<-[:REL]-(b)`
9. **Cache issues** - Restart `python src/main.py` after code changes (Python caches modules)
10. **Label filtering** - Use `:Item` in MATCH or `WHERE 'Item' IN labels(entity)` to filter node types
11. **Relationship-Types typo-prone** - Nutze Schema-Konstanten aus Notebook (REL_IST_IN, REL_ÖFFNET, etc.)
12. **IDs must be lowercase, no spaces** - Helper-Funktionen im Notebook erzwingen dies automatisch
13. **Property-Names sind case-sensitive** - `is_locked` nicht `is_Locked` oder `isLocked`
14. **Embedding matching ist teuer** - spaCy Model + SentenceTransformer = ~2s pro Input auf schwacher Hardware
15. **Logging-Config** - Mehrfaches `basicConfig()` in verschiedenen Modulen kann zu Konflikten führen

## Documentation

**Schema & Commands:**
- `docs/world_schema.md` - **START HERE** - Vollständiges Schema (Nodes, Relationships, Properties)
- `docs/commands.md` - Command-System (alle Commands, Verb-Mapping, Parser-Format)

**Technical Docs:**
- `docs/conversation_system.md` - ConversationSystem Architektur (Validierung, Rückfragen)
- `docs/neo4j_cheatsheet.md` - Cypher WHERE clause reference
- `docs/architecture_idea.md` - Original architecture vision (für Referenz)
- `docs/neo4j_docker.md` - Docker setup details

**General:**
- `README.md` - Setup instructions and roadmap
- `CLAUDE.md` - This file

**Notebooks:**
- `notebooks/01-neo4j_dbsetup.ipynb` - **Database initialization mit Helper-Funktionen**
- `notebooks/02-neo4j_commands.ipynb` - Query testing
- `notebooks/03-smart-parser.ipynb` - Smart Parser development & testing

## Future Roadmap Context

The codebase is designed to eventually support:
- LLM-based narrator (Ollama integration)
- NPC personalities with individual prompts
- Natural language parser (replacing current keyword parser)
- Command Pattern refactoring (currently flat if/elif in Controller)

When making changes, keep extensibility in mind but don't over-engineer for future phases.

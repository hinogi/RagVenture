# RagVenture - Architektur

Technische Dokumentation des Text-Adventure-Spiels. **Aktueller Stand.**

---

## Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         SPIELER                             │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     GAME CONTROLLER                         │
│  • Game Loop (State-Machine)                                │
│  • Orchestriert Parser, Model, View                         │
│  • Entity-Matching via EmbeddingUtils                       │
└──────┬──────────────────────────────┬───────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│   PARSER         │          │   GAME MODEL     │
│   (SmartParser)  │          │   (Neo4j)        │
│                  │          │                  │
│   spaCy NLP      │          │   DB Queries     │
│   → verb, noun   │          │   → Entities     │
└──────────────────┘          └──────────────────┘
       │                              │
       └──────────┬───────────────────┘
                  ▼
         ┌────────────────┐
         │   GAME VIEW    │
         │   (Rich UI)    │
         └────────────────┘
```

---

## GameState (State-Machine)

**Flache Struktur - alles in einer Dataclass:**

```python
class Status(Enum):
    PARSE = 'wait_for_parsing'    # Input → Verb/Noun
    VERIFY = 'wait_for_verify'    # Verb/Noun → Command/Target
    REQUEST = 'wait_for_answers'  # Rückfrage aktiv
    ACTION = 'wait_for_action'    # Bereit zur Ausführung

@dataclass
class GameState:
    running: bool = False
    loop_state: Status = Status.PARSE

    # Input & Parsing
    input: str | None = None
    verb: str | None = None
    noun: str | None = None

    # Matching-Ergebnisse
    command_list: list | None = None
    target_list: list | None = None

    # Feedback
    message: str | None = None
```

**State-Machine Flow:**

```
PARSE → verb/noun extrahieren
  ↓
VERIFY → command/target matchen
  ↓ (bei Mehrdeutigkeit)
REQUEST → Rückfrage anzeigen
  ↓
ACTION → Ausführen
  ↓
PARSE → Nächste Eingabe
```

---

## Game Loop

```python
while self.state.running:

    # 1. Render (DB ist Source of Truth)
    location = self.model.current_location()
    items = self.model.location_content()
    exits = self.model.location_exits()
    inventory = self.model.player_inventory()

    self.view.update_panels(location, items, exits, inventory, self.state.message)
    self.view.refresh()

    # 2. Input
    self.state.input = self.view.get_input()

    if self.state.input == 'quit':
        break

    # 3. State-Machine
    if self.state.loop_state == Status.PARSE:
        # Parser aufrufen
        parsed = self.parser_utils.parse(self.state.input)
        self.state.verb = parsed[0]['verb']
        self.state.noun = parsed[0]['noun']
        self.state.loop_state = Status.VERIFY

    if self.state.loop_state == Status.VERIFY:
        # Command matching
        commands = self.embedding_utils.verb_to_command(self.state.verb)
        good_commands = [c for c in commands if c['sim'] >= 0.95]

        # Target matching
        all_targets = self._handle_target_candidates(exits, items, inventory)
        matches = self.embedding_utils.match_entities(self.state.noun, all_targets)

        # Validierung...

    if self.state.loop_state == Status.REQUEST:
        # Rückfrage verarbeiten...

    if self.state.loop_state == Status.ACTION:
        # Ausführen...
```

---

## Target-Matching (alle Candidates)

```python
def _handle_target_candidates(self, exits, items, inventory):
    """Kombiniert alle Entities mit Type-Label"""
    candidates = []

    for e in exits:
        e['type'] = 'exit'
        candidates.append(e)
    for i in items:
        i['type'] = 'item'
        candidates.append(i)
    for i in inventory:
        i['type'] = 'inventory'
        candidates.append(i)

    return candidates
```

**Validierung:** Nach dem Matching prüfen ob `type` zum `command` passt:
- `go` + `exit` → ✓
- `go` + `item` → ✗ "Da kannst du nicht hingehen"
- `take` + `item` → ✓
- `take` + `exit` → ✗ "Das kannst du nicht nehmen"

---

## Datenfluss

```
User Input: "gehe zur taverne"
    ↓
Parser (spaCy)
    ↓
verb: "gehen", noun: "taverne"
    ↓
EmbeddingUtils.verb_to_command("gehen")
    ↓
[{'command': 'go', 'sim': 0.98}, ...]
    ↓
EmbeddingUtils.match_entities("taverne", candidates)
    ↓
[{'id': 'taverne', 'name': "Mo's Taverne", 'type': 'exit', 'score': 0.95}, ...]
    ↓
Validierung: command='go', type='exit' → ✓
    ↓
Model: move_player('taverne')
    ↓
View: "Du bist jetzt in Mo's Taverne"
```

---

## Terminologie

| Begriff | Bedeutung | Beispiel |
|---------|-----------|----------|
| **Input** | Rohe User-Eingabe | "gehe zur taverne" |
| **Verb** | Lemmatisiertes Verb (spaCy) | "gehen" |
| **Noun** | Extrahiertes Objekt (spaCy) | "taverne" |
| **Command** | System-Befehl | "go", "take", "drop" |
| **Target** | Gematchte Entity | `{'id': 'taverne', 'type': 'exit'}` |

---

## Thresholds

```python
COMMAND_THRESHOLD = 0.95   # Sehr hoch - nur sichere Matches
TARGET_THRESHOLD = 0.70    # Moderater - Typos erlaubt
```

- `>= 0.95` → Eindeutig
- Mehrere `>= threshold` → Rückfrage
- Keine `>= threshold` → Fehlermeldung

---

## Dateien

```
src/
├── controller/
│   └── game_controller.py    # Game Loop, State-Machine
├── model/
│   ├── game_state.py         # GameState + Status Enum
│   └── world_model.py        # Neo4j Repository
├── view/
│   └── game_view.py          # Rich UI
└── utils/
    ├── smart_parser.py       # spaCy NLP
    └── embedding_utils.py    # SentenceTransformer Matching
```

---

## Prinzipien

1. **DB ist Source of Truth** - Kein Caching, immer frisch laden
2. **State-Machine** - Explizite Zustände (PARSE, VERIFY, REQUEST, ACTION)
3. **Flacher State** - Alles in einer Dataclass, kein Nesting
4. **Controller orchestriert** - Parser, Model, View sind unabhängig
5. **Embeddings im Controller** - Matching-Logik nicht im Model

---

**Version:** 6.0 (Flat State-Machine)
**Aktualisierung:** 25. Dezember 2024

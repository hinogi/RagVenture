# RagVenture - Architektur-Übersicht

Dieses Dokument beschreibt die Idee der Architektur des Text-Adventure-Spiels. Gilt zur Orientierung, nicht als Vorlage.

---

## Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         SPIELER                             │
│                  (tippt Befehle ein)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     GAME CONTROLLER                         │
│  • Nimmt User Input entgegen                                │
│  • Koordiniert alle Komponenten                             │
│  • Game Loop                                                │
└──────┬──────────────────────────────┬───────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│     PARSER       │          │    GAME MODEL    │
│                  │          │                  │
│ "go north"       │          │  Neo4j Database  │
│      ↓           │          │                  │
│ ParsedCommand    │          │ • Player State   │
│ {                │          │ • Locations      │
│   verb: "go"     │          │ • Items          │
│   noun: "north"  │          │ • NPCs           │
│ }                │          │ • Relationships  │
└──────────────────┘          └──────────────────┘
       │                              │
       └──────────┬───────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   GAME VIEW    │
         │                │
         │  Rich Console  │
         │  • Output      │
         │  • Panels      │
         │  • Formatting  │
         └────────────────┘
```

---

## Die 4 Hauptkomponenten

**Update (Dezember 2024):** Mit Einführung des **ConversationSystem** haben wir jetzt 4 statt 3 Hauptkomponenten. Das ConversationSystem sitzt zwischen Parser und Controller und übernimmt die schrittweise Validierung von User-Eingaben mit Rückfragen.

### 1. PARSER (`src/utils/command_parser.py` / `SmartParser`)

**Aufgabe**: Natürliche Sprache → Strukturierte Parsing-Informationen

**WICHTIG:** Parser hat **KEINEN DB-Zugriff**! (MVC-Prinzip)

**Beispiele (Smart Parser):**
```python
Input:  "Nimm den goldenen Schlüssel"
Output: {
    'command': 'take',
    'confidence': 0.85,
    'object_text': 'Schlüssel',
    'adjectives': ['goldenen'],
    'raw': 'Nimm den goldenen Schlüssel',
    'verb_lemma': 'nehmen'
}

Input:  "Geh zur Taverne"
Output: {
    'command': 'visit',
    'confidence': 0.92,
    'object_text': 'Taverne',
    'adjectives': [],
    'raw': 'Geh zur Taverne',
    'verb_lemma': 'gehen'
}
```

**Funktionen:**
- **NLP mit SpaCy:** Verb-Extraktion, Objekt-Extraktion, Dependency Parsing
- **Intent Mapping:** Verb → Command via Sentence Transformers (Embeddings)
- **Synonym-Handling:** "nimm", "hol", "greif", "schnapp" → `'take'`
- **Adjektiv-Extraktion:** "goldenen alten Schlüssel" → `['goldenen', 'alten']`
- **Confidence-Score:** Wie sicher ist das Verb-Matching?
- **KEIN Entity-Matching:** Objekt-Text bleibt Text (z.B. "Schlüssel"), keine DB-IDs!

---

### 2. MODEL (`src/model/game_model.py`)

**Aufgabe**: Spielwelt-Zustand in Neo4j verwalten + Business Logic

**Verantwortlichkeiten:**
- ✅ **DB-Queries ausführen** (komplette Listen zurückgeben, nicht einzelne Matches)
- ✅ **Business-Validierung** (ist Item nehmbar? ist Location erreichbar?)
- ✅ **Aktionen ausführen** (take_item, drop_item, move_player)
- ❌ **KEIN Entity-Matching** (gehört in Controller - siehe Smart Parser Architecture)

**Kern-Funktionen:**

```python
# Player Operations
get_current_location() → {'id': 'taverne', 'name': 'Taverne', ...}
move_player(location_id) → True/False
get_player_inventory() → [Item, Item]

# Location Operations (liefern ALLE Entities)
get_items_at_location(location_id=None) → [
    {'id': 'fackel', 'name': 'Fackel', 'embedding': [...], ...},
    {'id': 'schluessel', 'name': 'Goldener Schlüssel', 'embedding': [...], ...}
]
get_npcs_at_location(location_id=None) → [NPC, NPC, ...]
get_exits(location_id=None) → [{'direction': 'north', 'target': 'cave', ...}, ...]

# Item Operations (mit DB-IDs)
take_item(item_id) → {'name': 'Fackel', ...} oder None
drop_item(item_id) → {'name': 'Fackel', ...} oder None

# NPC Operations
get_npc(npc_id) → NPC(name, dialogue)
talk_to_npc(npc_id) → "dialogue text"
```

**Neo4j Queries:**
- `MATCH (p:Player)-[:IST_IN]->(l:Location)` - Wo ist der Spieler?
- `MATCH (i:Item)-[:IST_IN]->(loc) RETURN i.id, i.name, i.name_embedding` - Alle Items am Ort (mit Embeddings!)
- `MATCH (l:Location)-[e:ERREICHT]->(l2:Location)` - Erreichbare Locations
- `MATCH (p:Player)-[:TRÄGT]->(i:Item)` - Inventar

**Wichtig:** Model gibt **komplette Listen** zurück, Matching passiert im Controller!

---

### 3. CONVERSATIONSYSTEM (`src/conversation/conversation_system.py`) **NEU**

**Aufgabe**: Validierung von User-Eingaben mit Rückfragen bei Mehrdeutigkeiten

**Verantwortlichkeiten:**
- ✅ **Command-Validierung** (Verb → Command mit Confidence-Checks)
- ✅ **Target-Validierung** (Noun → Entity mit Similarity-Checks)
- ✅ **Rückfragen stellen** (bei Mehrdeutigkeiten oder fehlenden Infos)
- ✅ **Action-Building** (vollständig validierte Action: Command + Targets)
- ✅ **Conversation-State** (pending_question für Multi-Turn-Dialoge)
- ❌ **KEINE Execution** (gehört in Controller)

**Kern-Konzept:**

ConversationSystem baut schrittweise eine **vollständig validierte Action** auf:
1. **Phase 1:** Verb → Command (mit Rückfragen bei Mehrdeutigkeit)
2. **Phase 2:** Noun → Target(s) (mit Rückfragen bei Mehrdeutigkeit)
3. **Phase 3:** Action Ready → zurück an Controller

**Beispiel-Flow:**
```python
# User: "gehe"
result = conversation.build_action("gehe")
# → status='needs_clarification', question='Wohin?', options=[taverne, wald]

# User wählt: "1"
result = conversation.build_action("1")
# → status='action_ready', action=Action(command='go', targets=[taverne])

# Controller führt aus:
output = controller.execute_action(result.action)
```

**Datenstrukturen:**
```python
@dataclass
class Action:
    command: str           # 'go', 'take', 'drop', etc.
    targets: List[dict]    # [{'id': '...', 'name': '...'}]
    verb: str             # Original (für Logging)
    noun: str | None      # Original (für Logging)

@dataclass
class ConversationResult:
    status: str                    # 'action_ready', 'needs_clarification', 'error'
    action: Action | None          # Bei action_ready
    question: str | None           # Bei needs_clarification
    options: List[dict] | None     # Bei needs_clarification
    message: str | None            # Bei error
```

**Validierungs-Schwellwerte:**
```python
COMMAND_SIMILARITY_THRESHOLD = 0.95   # Command muss sehr sicher sein
TARGET_SIMILARITY_THRESHOLD = 0.70    # Target darf flexibler sein
AMBIGUITY_GAP = 0.05                  # Min. Abstand für Eindeutigkeit
```

**Details:** Siehe `docs/conversation_system.md`

---

### 4. GAME CONTROLLER (`src/controller/game_controller.py`)

**Aufgabe**: Orchestriert alle Komponenten + führt Actions aus

**Verantwortlichkeiten (VEREINFACHT mit ConversationSystem!):**
- ✅ **Game Loop** (UI Updates, Input holen, Output anzeigen)
- ✅ **ConversationSystem → Model → View koordinieren**
- ✅ **Action Execution** (nimmt validierte Action, führt via Model aus)
- ✅ **Game State Management** (cached current_location, exits, items, inventory)
- ❌ **KEINE Validierung** (macht jetzt ConversationSystem)
- ❌ **KEINE Business-Logik** (gehört ins Model)

**Merksatz (NEU):**
> **Parser versteht Sprache. ConversationSystem validiert. Controller orchestriert. Model verwaltet Daten und Regeln.**

**Pseudo-Code (NEUE ARCHITEKTUR mit ConversationSystem):**
```python
def run_game(self):
    """Hauptloop mit ConversationSystem"""
    conversation = ConversationSystem(
        parser=self.parser,
        embedding_utils=self.embedding_utils,
        game_state_provider=lambda: self.game_state
    )

    while self.game_running:
        # 1. UI Update
        self._update_game_state()  # Lädt exits, items, inventory aus Model
        self.view.update_panels(**self.game_state)

        # 2. Input holen (Prompt je nach Conversation-State)
        prompt = "→ " if conversation.has_pending_question() else "> "
        user_input = self.view.get_input(prompt)

        # 3. Quit-Check
        if user_input == 'quit':
            break

        # 4. ConversationSystem baut Action (mit Rückfragen)
        result = conversation.build_action(user_input)

        # 5. Rückfrage?
        if result.status == 'needs_clarification':
            self.view.show_question(result.question, result.options)
            continue  # Nächste Iteration holt Antwort

        # 6. Error?
        if result.status == 'error':
            self.view.show_message(result.message)
            continue

        # 7. Action Ready → Ausführen!
        if result.status == 'action_ready':
            output = self._execute_action(result.action)
            self.view.show_message(output)

def _execute_action(self, action: Action):
    """Führt validierte Action aus"""
    if action.command == 'go':
        result = self.model.move_player(action.targets[0]['id'])
        if result:
            return f"Du bist jetzt in {result[0]['name']}"
        else:
            return "Du kannst da nicht hin."

    elif action.command == 'take':
        result = self.model.take_item(action.targets[0]['id'])
        if result:
            return f"Du trägst jetzt {result[0]['name']}"
        else:
            return "Das kannst du nicht nehmen."

    # ... weitere Commands
```

**Faustregel (ERWEITERT):**
> Alles was mit **Daten und Logik** zu tun hat → **Model**.
> Alles was **Ablauf und UI** betrifft → **Controller**.
> Alles was **Text-Verständnis** betrifft → **Parser**.
> Alles was **Validierung und Rückfragen** betrifft → **ConversationSystem**.

---

## Konkreter Workflow (Beispiel)

**Spieler tippt:** `"geh nach norden"`

```
1. Controller empfängt Input
   ↓
2. Parser verarbeitet:
   "geh nach norden"
   → ParsedCommand(verb="go", noun="north")
   ↓
3. Controller validiert:
   ✓ Befehl ist vollständig
   ✓ "go" braucht eine Richtung → vorhanden
   ↓
4. Controller ruft Model:
   success = model.move_player("north")
   ↓
5. Model führt Neo4j Query aus:
   - Wo ist Player? → "forest_entrance"
   - Gibt es Exit "north"?
     MATCH (current:Location {id: 'forest_entrance'})
           -[e:ERREICHT {direction: 'north'}]->
           (target:Location)
   - Ja → "dark_cave" gefunden
   - UPDATE Player Relationship
   ↓
6. Model gibt zurück:
   success = True
   ↓
7. Controller holt neue Location Details:
   location = model.get_location_info("dark_cave")
   → Location(
       name="Dunkle Höhle",
       description="Es ist kalt und dunkel...",
       exits=["south", "east"]
     )
   ↓
8. Controller gibt an View:
   view.show_location(location)
   ↓
9. Rich Console zeigt:
   ┌─ Dunkle Höhle ────────────┐
   │ Es ist kalt und dunkel... │
   │                            │
   │ Ausgänge: süd, ost        │
   └───────────────────────────┘
```

---

## Build-Reihenfolge

### Phase 1: Parser (isoliert testbar)
- **Input**: String
- **Output**: ParsedCommand
- **Dependencies**: Keine
- **Testbar**: Ja, ohne DB

### Phase 2: Model (braucht Neo4j)
- **Input**: Method Calls
- **Output**: Game State
- **Dependencies**: Neo4j Connection
- **Testbar**: Ja, mit Test-DB

### Phase 3: Controller erweitern
- **Input**: User Input
- **Output**: View Calls
- **Dependencies**: Parser + Model + View
- **Aufgabe**: Command Dispatcher implementieren

### Phase 4: View erweitern
- **Input**: Structured Data
- **Output**: Rich Console Output
- **Methoden**:
  - `show_location(location)`
  - `show_inventory(items)`
  - `show_error(message)`
  - `show_npc_dialogue(npc, text)`

---

## Datenfluss-Diagramm (mit ConversationSystem)

```
User Input
    ↓
[Parser] → verb, noun, raw
    ↓
[ConversationSystem] → validates step-by-step
    ├─ Phase 1: Verb → Command
    │  └─ Mehrdeutig? → Rückfrage → User antwortet → Loop
    │
    ├─ Phase 2: Noun → Target(s)
    │  └─ Mehrdeutig? → Rückfrage → User antwortet → Loop
    │
    └─ Phase 3: Action Ready
        ↓
[Controller] → execute_action(action)
    ↓
[Model] ← → [Neo4j Database]
    ↓
[Controller] ← returns data
    ↓
[View] → Rich Console Output
    ↓
User sees result
```

**Wichtig:** Rückfragen-Loop kann mehrere Iterationen brauchen, bis Action vollständig ist.

---

## Design Patterns

- **MVC Pattern**: Model-View-Controller Separation
- **Command Pattern**: Jeder Befehl ist strukturiert
- **Repository Pattern**: Model abstrahiert DB-Zugriffe
- **Facade Pattern**: Controller vereinfacht Interaktionen

---

---

## Wichtige Architektur-Änderungen (Dezember 2024)

### Separation of Concerns: Wer macht was?

**Alte Architektur (ursprüngliche Idee):**
- Parser: String-Splitting
- Controller: Command-Mapping + Routing
- Model: DB + Matching

**Neue Architektur (Smart Parser):**
- **Parser:** NLP (SpaCy) + Command-Mapping (Embeddings) → **KEIN DB-Zugriff**
- **Controller:** Orchestrierung + Entity-Matching (Similarity) + Entscheidungen
- **Model:** DB-Operations (komplette Listen) + Business-Validierung → **KEIN Matching**

**Warum?**
- ✅ Parser isoliert testbar (ohne Neo4j)
- ✅ Model einfacher (nur Daten, keine Matching-Logik)
- ✅ Controller hat volle Kontrolle über Entscheidungen (Confidence-Thresholds, Dialoge)
- ✅ Klare Verantwortlichkeiten (MVC-Pattern eingehalten)

### Verwandte Dokumente

- `conversation_system.md` - **NEU** - Detaillierte ConversationSystem-Architektur (Validierung, Rückfragen, Action-Building)
- `commands.md` - Command-Referenz mit Disambiguation-Patterns
- `world_schema.md` - Neo4j Graph-Schema
- `neo4j_cheatsheet.md` - Cypher-Query-Referenz
- `CLAUDE.md` - Aktuelle Projekt-Instruktionen

---

**Status**: Living Document
**Letzte Aktualisierung**: 18. Dezember 2024
**Version**: MVP Phase 1 + Smart Parser + ConversationSystem

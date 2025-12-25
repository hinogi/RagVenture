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

### 3. STATE-MANAGEMENT (Statechart-Ready Dataclasses) **NEU**

**Aufgabe**: Spielzustand und Conversation-State als Dataclasses mit Methoden

**Architektur-Prinzip: DB ist Single Source of Truth**
```
┌─────────────────────────────────────────────────┐
│                   GameState                      │
│  running: bool                                   │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │         ConversationState               │    │
│  │  status: Enum (PROMPT / REQUEST)        │    │
│  │  question, options                      │    │
│  │  pending_command, pending_verb,         │    │
│  │  pending_noun                           │    │
│  │                                         │    │
│  │  ask(), reset(), is_waiting()           │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  start(), stop()                                 │
└─────────────────────────────────────────────────┘

World-Daten → direkt vom Model (Neo4j)
```

**Dateien:**
- `src/model/game_state.py` - GameState Container (running + conversation)
- `src/model/conversation_state.py` - ConversationState + Status Enum

**Verantwortlichkeiten:**
- ✅ **State-Container** (ein `GameState` mit ConversationState)
- ✅ **Dataclasses mit Methoden** (Logik gekapselt: `ask()`, `reset()`, `is_waiting()`)
- ✅ **pending_* Fields** für Kontext bei Rückfragen
- ✅ **field(default_factory=...)** für korrekte mutable Defaults
- ❌ **KEIN WorldState-Caching** (DB ist Source of Truth)
- ❌ **KEINE Business-Logik** (gehört in Controller/Model)

**Beispiel-Flow:**
```python
# Controller initialisiert
self.state = GameState()
self.state.start()

# World-Daten direkt vom Model (kein Caching!)
items = self.model.location_content()
exits = self.model.location_exits()

# Rückfrage stellen (mit Kontext)
self.state.conversation.pending_command = 'go'
self.state.conversation.ask("Wohin?", exits)

# Check ob Rückfrage aktiv → Handler-Dispatch
if self.state.conversation.is_waiting():
    self._handle_choice(user_input)
else:
    self._handle_command(user_input)

# Zurücksetzen (inkl. pending_*)
self.state.conversation.reset()
```

**Validierung passiert im Controller** mit zwei Handlern.

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
> **Parser versteht Sprache. State speichert. Controller orchestriert. Model verwaltet Daten.**

**Game Loop Phasen:**

```
┌─────────────────────────────────────────┐
│  PHASE 1: Setup                         │
│  - State starten                        │
│  - Welcome zeigen                       │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  PHASE 2: Update & Render               │◄──┐
│  - World-State laden                    │   │
│  - View aktualisieren                   │   │
└────────────────┬────────────────────────┘   │
                 ▼                            │
┌─────────────────────────────────────────┐   │
│  PHASE 3: Input                         │   │
│  - Prompt anzeigen (> oder →)           │   │
│  - User-Input holen                     │   │
└────────────────┬────────────────────────┘   │
                 ▼                            │
┌─────────────────────────────────────────┐   │
│  PHASE 4: Quit?                         │   │
│  - Wenn quit → raus                     │   │
└────────────────┬────────────────────────┘   │
                 ▼                            │
┌─────────────────────────────────────────┐   │
│  PHASE 5: Rückfrage aktiv?              │   │
│  - Wenn ja → Auswahl/Abbruch handeln    │   │
│  - Dann zurück zu Phase 2               │   │
└────────────────┬────────────────────────┘   │
                 ▼                            │
┌─────────────────────────────────────────┐   │
│  PHASE 6: Parse & Match                 │   │
│  - Verb/Noun extrahieren                │   │
│  - Command matchen                      │   │
└────────────────┬────────────────────────┘   │
                 ▼                            │
┌─────────────────────────────────────────┐   │
│  PHASE 7: Validate & Execute            │   │
│  - Command validieren                   │   │
│  - Bei Mehrdeutigkeit → Rückfrage       │   │
│  - Sonst → Ausführen                    │   │
└────────────────┴────────────────────────┘───┘
```

**Pseudo-Code (Two-Handler Pattern):**
```python
def run_game(self):
    # ══════════════════════════════════════
    # PHASE 1: Setup
    # ══════════════════════════════════════
    self.state.start()
    self.view.show_welcome()
    input()  # Warte auf Enter

    while self.state.running:
        # ══════════════════════════════════════
        # PHASE 2: Update & Render (DB ist Source of Truth)
        # ══════════════════════════════════════
        self._update_view()  # Holt Daten direkt vom Model

        # ══════════════════════════════════════
        # PHASE 3: Input
        # ══════════════════════════════════════
        prompt = "→ " if self.state.conversation.is_waiting() else "> "
        user_input = self.view.get_input(prompt)

        # ══════════════════════════════════════
        # PHASE 4: Quit?
        # ══════════════════════════════════════
        if user_input.lower() == 'quit':
            self.state.stop()
            break

        # ══════════════════════════════════════
        # PHASE 5-7: Handler-Dispatch (zwei Modi)
        # ══════════════════════════════════════
        if self.state.conversation.is_waiting():
            self._handle_choice(user_input)  # Rückfrage-Modus
        else:
            self._handle_command(user_input)  # Normal-Modus


def _handle_choice(self, user_input):
    """Rückfrage-Modus: Auswahl oder Abbruch"""
    if user_input.lower() in ['abbrechen', 'cancel']:
        self.state.conversation.reset()
        return

    # Nummer → Auswahl aus options
    try:
        choice = int(user_input) - 1
        options = self.state.conversation.options
        if 0 <= choice < len(options):
            selected = options[choice]
            command = self.state.conversation.pending_command
            self.state.conversation.reset()
            self._execute_action(command, selected)
    except ValueError:
        self.view.show_message("Bitte eine Nummer eingeben.")


def _handle_command(self, user_input):
    """Normal-Modus: Parse → Match → Execute"""
    parsed = self.parser_utils.parse(user_input)
    verb, noun = parsed[0]['verb'], parsed[0]['noun']

    commands = self.embedding_utils.verb_to_command(verb)
    good_commands = [c for c in commands if c['sim'] >= 0.95]

    if len(good_commands) == 0:
        self.view.show_message(f"Ich verstehe '{verb}' nicht.")
        return

    if len(good_commands) > 1:
        self.state.conversation.pending_verb = verb
        self.state.conversation.ask("Was möchtest du tun?", good_commands)
        return

    command = good_commands[0]['command']
    # Entity-Matching und Execute...

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
> Alles was mit **Daten und Logik** zu tun hat → **Model** (DB ist Source of Truth).
> Alles was **Ablauf und UI** betrifft → **Controller** (zwei Handler für saubere Trennung).
> Alles was **Text-Verständnis** betrifft → **Parser** (spaCy + Embeddings).
> Alles was **State-Management** betrifft → **Dataclasses** (GameState + ConversationState).

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

- `conversation_system.md` - Statechart-Ready Architektur (State-Dataclasses, Validierung, Rückfragen)
- `commands.md` - Command-Referenz mit Disambiguation-Patterns
- `world_schema.md` - Neo4j Graph-Schema
- `CLAUDE.md` - Aktuelle Projekt-Instruktionen

---

**Status**: Living Document
**Letzte Aktualisierung**: 24. Dezember 2024
**Version**: MVP Phase 1 + Smart Parser + Two-Handler Pattern (DB ist Source of Truth)

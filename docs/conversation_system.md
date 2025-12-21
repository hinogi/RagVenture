# ConversationSystem - Action-Validierung mit Rückfragen

## Übersicht

**Statechart-Ready Architektur:** Ein GameState Container mit parallelen Regionen (WorldState + ConversationState). Dataclasses mit Methoden für gekapselte Logik. Controller orchestriert und ruft Parser/EmbeddingUtils selbst auf.

**Datei-Struktur:**
```
src/model/
├── game_state.py           # GameState Container (mit WorldState, ConversationState, Status Enum)
├── world_model.py          # Neo4j Repository

src/utils/
├── conversation_system.py  # ConversationUtils (minimal - nur has_pending_question)
├── smart_parser.py         # SmartParserUtils
└── embedding_utils.py      # EmbeddingUtils
```

---

## Terminologie / Wording

```
User Input: "gehe zur taverne"
    ↓
Parsing (spaCy)
    ↓
├─ Verb: "gehen"      (linguistisch, lemmatisiert)
└─ Noun: "taverne"    (linguistisch)
    ↓
Command Matching (Embeddings)
    ↓
Command: "go"         (System-Befehl)
    ↓
Target Matching (Embeddings)
    ↓
Target: {id: 'taverne', name: "Mo's Taverne"}
    ↓
Action: Command + Target(s)
    ↓
Execution → Model → View
```

### Begriffsdefinitionen

| Begriff | Bedeutung | Beispiel |
|---------|-----------|----------|
| **User Input** | Rohe Eingabe vom User | "gehe zur taverne" |
| **Verb** | Linguistisches Verb (lemmatisiert, spaCy) | "gehen" |
| **Noun** | Linguistisches Objekt (spaCy) | "taverne" |
| **Command** | System-Befehl, den das Game versteht | "go" |
| **Target** | Konkretes Game-Entity aus game_state | `{'id': 'taverne', 'name': "Mo's Taverne"}` |
| **Action** | Vollständig validierte Aktion (Command + Targets) | `Action{command: 'go', targets: [taverne]}` |

**Wichtig:** Diese Terminologie wird im gesamten Code verwendet, um Missverständnisse zu vermeiden.

---

## Architektur

### Aktueller Zustand (ohne ConversationSystem)

```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Parser    │ ← spaCy + Embeddings
│  (Smart)     │   Gibt: verb, noun, raw
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           Controller                         │
│  • Entity-Matching (verb→cmd, noun→target)   │
│  • Confidence/Threshold Checks               │
│  • Command Routing (if/elif)                 │
│  • Game State Updates                        │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────┐         ┌──────────────┐
│    Model     │────────▶│    View      │
│  (Neo4j)     │         │   (Rich UI)  │
└──────────────┘         └──────────────┘
```

**Problem:** Controller macht zu viel - Parsing-Logik, Validierung, Rückfragen, Execution alles vermischt.

---

### Neuer Zustand (mit ConversationSystem)

```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│                    Controller                        │
│  (Orchestriert alles)                                │
│                                                      │
│  1. Parser aufrufen                                  │
│     parsed = self.parser.parse(input)                │
│     verb, noun = parsed[0]['verb'], parsed[0]['noun']│
│                                                      │
│  2. Command-Matching                                 │
│     command_matches = embedding_utils.verb_to_command│
│                                                      │
│  3. ConversationSystem: Command validieren           │
│     ┌─────────────────────────────────────────┐     │
│     │  validate_command(verb, command_matches) │     │
│     │  → Threshold-Check, Mehrdeutigkeit       │     │
│     │  → Bei Rückfrage: pending_question setzen│     │
│     └─────────────────────────────────────────┘     │
│                                                      │
│  4. Entity-Matching                                  │
│     entity_matches = embedding_utils.match_entities  │
│                                                      │
│  5. ConversationSystem: Target validieren            │
│     ┌─────────────────────────────────────────┐     │
│     │  validate_target(noun, entity_matches)   │     │
│     │  → Threshold-Check, Mehrdeutigkeit       │     │
│     │  → Bei Rückfrage: pending_question setzen│     │
│     └─────────────────────────────────────────┘     │
│                                                      │
│  6. Action ausführen                                 │
│     output = self._execute_action(action)            │
│                                                      │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐         ┌──────────────┐
│    Model     │────────▶│    View      │
└──────────────┘         └──────────────┘
```

**Vorteile:**
- ✅ **Controller bleibt Orchestrator** - Ruft Parser, EmbeddingUtils, ConversationSystem auf
- ✅ **ConversationSystem ist schlank** - Nur Validierung + State, keine Abhängigkeiten
- ✅ **Testbar** - ConversationSystem mit Mock-Daten testbar
- ✅ **Keine Überladung** - Jede Komponente hat klare Verantwortung

---

## Conversation Flow

### Happy Path (keine Rückfragen nötig)

```
User: "gehe zur taverne"
  ↓
Parser: verb="gehen", noun="taverne"
  ↓
ConversationSystem:
  Phase 1: verb_to_command("gehen")
    → [{'command': 'go', 'sim': 0.999}]  ✅ Eindeutig (>0.95)

  Phase 2: match_entities("taverne", exits)
    → [{'id': 'taverne', 'score': 0.95}]  ✅ Eindeutig

  Phase 3: Action Ready
    → Action{command: 'go', targets: [taverne]}
  ↓
Controller: execute_action(action)
  → model.move_player('taverne')
  ↓
View: "Du bist jetzt in Mo's Taverne"
```

**Dauer:** ~1 Input, ~2 Sekunden

---

### Rückfrage: Fehlendes Noun

```
User: "gehe"
  ↓
Parser: verb="gehen", noun=None
  ↓
ConversationSystem:
  Phase 1: ✅ Command "go" eindeutig
  Phase 2: ❌ Kein Noun vorhanden
    → RETURN: ConversationResult(
        status='needs_clarification',
        question='Wohin möchtest du gehen?',
        options=[taverne, wald, schmiede]
      )
  ↓
View:
  "Wohin möchtest du gehen?"
  [1] Mo's Taverne
  [2] Finsterwald
  [3] Schmiede

Prompt: "→ "  (statt "> ")
  ↓
User: "2"
  ↓
ConversationSystem: resolve_question(choice=2)
  → Wählt options[1] = wald
  Phase 2: ✅ Target gefunden
  Phase 3: Action Ready
    → Action{command: 'go', targets: [wald]}
  ↓
Controller: execute_action(action)
  → model.move_player('wald')
  ↓
View: "Du bist jetzt im Finsterwald"
```

**Dauer:** 2 Inputs (Original + Antwort)

---

### Rückfrage: Mehrdeutige Entities

```
User: "nimm schlüssel"
  ↓
Parser: verb="nimm", noun="schlüssel"
  ↓
ConversationSystem:
  Phase 1: ✅ Command "take" eindeutig
  Phase 2: match_entities("schlüssel", items)
    → [
        {'id': 'rostiger_schluessel', 'name': 'Rostiger Schlüssel', 'score': 0.85},
        {'id': 'goldener_schluessel', 'name': 'Goldener Schlüssel', 'score': 0.83}
      ]
    → Beide > Threshold (0.70)! ❌ Mehrdeutig
    → RETURN: ConversationResult(
        status='needs_clarification',
        question='Welchen Schlüssel meinst du?',
        options=[rostiger_schluessel, goldener_schluessel]
      )
  ↓
View:
  "Welchen Schlüssel meinst du?"
  [1] Rostiger Schlüssel (alt und verbeult)
  [2] Goldener Schlüssel (glänzt prächtig)

Prompt: "→ "
  ↓
User: "2"
  ↓
ConversationSystem: resolve_question(choice=2)
  → Wählt options[1] = goldener_schluessel
  Phase 2: ✅ Target eindeutig
  Phase 3: Action Ready
    → Action{command: 'take', targets: [goldener_schluessel]}
  ↓
Controller: execute_action(action)
  → model.take_item('goldener_schluessel')
  ↓
View: "Du trägst jetzt Goldener Schlüssel"
```

---

### Rückfrage: Mehrdeutige Commands

```
User: "mach feuer"
  ↓
Parser: verb="mach", noun="feuer"
  ↓
ConversationSystem:
  Phase 1: verb_to_command("mach")
    → [
        {'command': 'use', 'sim': 0.96},
        {'command': 'examine', 'sim': 0.95}
      ]
    → Beide > Threshold (0.95)! ❌ Mehrdeutig
    → RETURN: ConversationResult(
        status='needs_clarification',
        question='Was möchtest du tun?',
        options=['use', 'examine']
      )
  ↓
View:
  "Was möchtest du tun?"
  [1] benutzen (use)
  [2] untersuchen (examine)

Prompt: "→ "
  ↓
User: "1"
  ↓
ConversationSystem: resolve_question(choice=1)
  → Wählt options[0] = 'use'
  Phase 1: ✅ Command eindeutig
  Phase 2: ... (weiter zu Target-Validierung)
```

---

### Abbrechen

```
User: "gehe"
  ↓
ConversationSystem:
  Phase 2: ❌ Kein Noun
  → Rückfrage: "Wohin?"
  ↓
View:
  "Wohin möchtest du gehen?"
  [1] Taverne
  [2] Wald

Prompt: "→ "
  ↓
User: "abbrechen"
  ↓
ConversationSystem:
  if user_input.lower() in ['abbrechen', 'zurück', 'cancel']:
      conversation.reset()
      return ConversationResult(
          status='cancelled',
          message='Abgebrochen.'
      )
  ↓
View: "Abgebrochen."
Prompt: "> "  (zurück zu Normal)
```

---

## Datenstrukturen

### Action (vollständig validierte Aktion)

```python
@dataclass
class Action:
    """Vollständig validierte Spielaktion, bereit zur Ausführung"""
    command: str              # 'go', 'take', 'drop', 'use', etc.
    targets: List[dict]       # Entities: [{'id': '...', 'name': '...', ...}]
    verb: str                 # Original verb (für Logging/Debug)
    noun: str | None          # Original noun (für Logging/Debug)
```

**Beispiele:**
```python
# Bewegung
Action(command='go', targets=[{'id': 'taverne', 'name': "Mo's Taverne"}], verb='gehen', noun='taverne')

# Item aufnehmen
Action(command='take', targets=[{'id': 'schwert', 'name': 'Rostiges Schwert'}], verb='nimm', noun='schwert')

# Item benutzen (mit Target)
Action(command='use', targets=[
    {'id': 'schluessel', 'name': 'Goldener Schlüssel'},
    {'id': 'truhe', 'name': 'Verschlossene Truhe'}
], verb='benutze', noun='schlüssel')
```

---

### ConversationResult (Return-Wert von ConversationSystem)

```python
@dataclass
class ConversationResult:
    """Return-Wert von ConversationSystem.build_action()"""
    status: str               # 'action_ready', 'needs_clarification', 'error', 'cancelled'

    # Bei action_ready:
    action: Action | None = None

    # Bei needs_clarification:
    question: str | None = None
    options: List[dict] | None = None  # [{'id': '...', 'name': '...', 'description': '...'}]

    # Bei error:
    message: str | None = None
```

**Beispiele:**
```python
# Action bereit
ConversationResult(
    status='action_ready',
    action=Action(command='go', targets=[...], verb='gehen', noun='taverne')
)

# Rückfrage nötig
ConversationResult(
    status='needs_clarification',
    question='Wohin möchtest du gehen?',
    options=[
        {'id': 'taverne', 'name': "Mo's Taverne", 'description': 'Eine gemütliche Kneipe'},
        {'id': 'wald', 'name': 'Finsterwald', 'description': 'Dunkel und gefährlich'}
    ]
)

# Fehler
ConversationResult(
    status='error',
    message="Ich verstehe 'tanzen' nicht."
)

# Abgebrochen
ConversationResult(
    status='cancelled',
    message='Abgebrochen.'
)
```

---

### ConversationSystem (schlank)

```python
class ConversationSystem:
    """Nur State + Validierung - KEINE Abhängigkeiten zu Parser/EmbeddingUtils"""

    def __init__(self):
        self.pending_question = None
        # {
        #   'type': 'command' | 'target',
        #   'command': str,           # Bei target-Rückfrage
        #   'verb': str,              # Original verb
        #   'noun': str | None,       # Original noun
        #   'options': [...]          # Zur Auswahl
        # }

    def has_pending_question(self) -> bool:
        """Check ob Rückfrage aktiv"""
        return self.pending_question is not None

    def reset(self):
        """Setzt Conversation State zurück"""
        self.pending_question = None

    # Bekommt fertige Daten vom Controller:
    def validate_command(self, verb: str, command_matches: list) -> ConversationResult
    def validate_target(self, noun: str, entity_matches: list, command: str) -> ConversationResult
    def resolve_choice(self, choice: int) -> ConversationResult
```

---

## Game Loop Integration

### Pseudo-Code (neuer Game Loop)

**Controller orchestriert - ConversationSystem nur für Validierung:**

```python
def run_game(self):
    while self.game_running:
        self._update_game_state()

        # Prompt wechseln bei Rückfrage
        prompt = "→ " if self.conversation.has_pending_question() else "> "
        user_input = self.view.get_input(prompt)

        # Quit-Check
        if user_input.lower() == 'quit':
            break

        # Abbrechen-Check
        if self.conversation.has_pending_question():
            if user_input.lower() in ['abbrechen', 'zurück', 'cancel']:
                self.conversation.reset()
                self._update_game_state(conversation="Abgebrochen.")
                continue

        # Pending Question? → Auflösen
        if self.conversation.has_pending_question():
            result = self.conversation.resolve_choice(user_input)
            # ... handle result
            continue

        # === CONTROLLER ORCHESTRIERT ===

        # 1. Parser aufrufen
        parsed = self.parser.parse(user_input)
        verb, noun = parsed[0]['verb'], parsed[0]['noun']

        # 2. Command-Matching
        command_matches = self.embedding_utils.verb_to_command(verb)

        # 3. Command validieren (ConversationSystem)
        result = self.conversation.validate_command(verb, command_matches)
        if result.status == 'needs_clarification':
            self._update_game_state(conversation=self._format_question(result))
            continue
        if result.status == 'error':
            self._update_game_state(conversation=result.message)
            continue

        command = result.command

        # 4. Entity-Matching
        candidates = self._get_candidates(command)
        entity_matches = self.embedding_utils.match_entities(noun, candidates)

        # 5. Target validieren (ConversationSystem)
        result = self.conversation.validate_target(noun, entity_matches, command)
        if result.status == 'needs_clarification':
            self._update_game_state(conversation=self._format_question(result))
            continue
        if result.status == 'error':
            self._update_game_state(conversation=result.message)
            continue

        # 6. Action ausführen
        output = self._execute_action(result.action)
        self._update_game_state(conversation=output)
```

---

## Design-Entscheidungen

### 1. Antwort-Format bei Rückfragen

**Entscheidung:** Nummerierte Auswahl (1, 2, 3)

**Begründung:**
- ✅ Einfach und schnell für User
- ✅ Eindeutig zu parsen (Integer)
- ✅ Keine Embedding-Matches nötig bei Antworten
- ❌ Weniger "natürlich" als Freitext

**Implementierung:**
```python
# View zeigt:
"Welchen Schlüssel meinst du?"
[1] Rostiger Schlüssel
[2] Goldener Schlüssel

# User antwortet:
user_input = "2"

# Parser:
try:
    choice = int(user_input) - 1  # 0-indexed
    if 0 <= choice < len(options):
        selected = options[choice]
except ValueError:
    # Nicht numerisch → Error
    return "Bitte wähle eine Nummer (1, 2, ...)"
```

---

### 2. Abbrechen-Funktion

**Entscheidung:** User kann mit 'abbrechen', 'zurück', 'cancel' raus

**Begründung:**
- ✅ User hat Kontrolle, fühlt sich nicht "gefangen"
- ✅ Bei Tippfehler oder falscher Eingabe einfach neu starten
- ❌ Mehr Code-Komplexität (Check in jeder Rückfrage-Phase)

**Implementierung:**
```python
CANCEL_KEYWORDS = ['abbrechen', 'zurück', 'cancel', 'stop']

if conversation.has_pending_question():
    if user_input.lower() in CANCEL_KEYWORDS:
        conversation.reset()
        return "Abgebrochen."
```

---

### 3. Schwellwerte (Thresholds)

**Entscheidung:** Erstmal als Konstanten, später optional Config

**Werte:**
```python
COMMAND_SIMILARITY_THRESHOLD = 0.95   # Sehr hoch - nur sichere Matches
TARGET_SIMILARITY_THRESHOLD = 0.70    # Moderater - mehr Flexibilität
AMBIGUITY_GAP = 0.05                  # Min. Abstand für Eindeutigkeit
```

**Begründung:**
- Command-Matching muss sehr sicher sein → 0.95
- Target-Matching darf flexibler sein (Typos, Synonyme) → 0.70
- Bei mehreren ähnlichen Matches (Gap < 0.05) → Rückfrage

**Beispiel:**
```python
matches = [
    {'command': 'go', 'sim': 0.97},
    {'command': 'take', 'sim': 0.93}  # < 0.95, fällt raus
]
→ Eindeutig: 'go'

matches = [
    {'command': 'go', 'sim': 0.97},
    {'command': 'use', 'sim': 0.96}   # Gap = 0.01 < 0.05
]
→ Mehrdeutig! Rückfrage
```

---

### 4. State Persistence

**Entscheidung:** Nicht in dieser Phase

**Begründung:**
- Conversation State ist Session-lokal (in-memory)
- Kein Speichern über Game-Sessions hinweg nötig
- Bei Quit → State verloren (kein Problem)

**Später optional:** NPC-Dialoge könnten persistent sein (Quest-Progress etc.)

---

## Validierungs-Methoden (Details)

### validate_command()

**Eingabe:** `verb` (aus Parser), `command_matches` (aus EmbeddingUtils)
**Ausgabe:** `ConversationResult` mit `command` oder Rückfrage

**Wichtig:** Controller ruft `embedding_utils.verb_to_command(verb)` auf und gibt Ergebnis weiter!

```python
def validate_command(self, verb: str, command_matches: list) -> ConversationResult:
    # 1. Verb vorhanden?
    if not verb:
        return ConversationResult(
            status='error',
            message='Was möchtest du tun?'
        )

    # 2. Filtern nach Threshold
    good_matches = [m for m in command_matches if m['sim'] >= COMMAND_THRESHOLD]

    # 3. Kein Match?
    if len(good_matches) == 0:
        return ConversationResult(
            status='error',
            message=f"Ich verstehe '{verb}' nicht."
        )

    # 4. Mehrdeutig?
    if len(good_matches) > 1:
        self.pending_question = {
            'type': 'command',
            'verb': verb,
            'options': good_matches
        }
        return ConversationResult(
            status='needs_clarification',
            question='Was möchtest du tun?',
            options=good_matches
        )

    # 5. Eindeutig!
    return ConversationResult(
        status='command_ready',
        command=good_matches[0]['command']
    )
```

---

### validate_target()

**Eingabe:** `noun` (aus Parser), `entity_matches` (aus EmbeddingUtils), `command`
**Ausgabe:** `ConversationResult` mit `action` oder Rückfrage

**Wichtig:** Controller ruft `embedding_utils.match_entities(noun, candidates)` auf und gibt Ergebnis weiter!

```python
def validate_target(self, noun: str, entity_matches: list, command: str) -> ConversationResult:
    # 1. Kein Noun und keine Matches? → Rückfrage mit allen Optionen
    if not noun and not entity_matches:
        return ConversationResult(
            status='needs_clarification',
            question=self._get_target_question(command),
            options=[]  # Controller muss candidates liefern
        )

    # 2. Keine Matches gefunden?
    if not entity_matches:
        return ConversationResult(
            status='error',
            message=f"Ich kann '{noun}' nicht finden."
        )

    # 3. Filtern nach Threshold
    good_matches = [m for m in entity_matches if m['score'] >= TARGET_THRESHOLD]

    # 4. Kein guter Match?
    if len(good_matches) == 0:
        return ConversationResult(
            status='error',
            message=f"Ich bin mir nicht sicher was '{noun}' sein soll."
        )

    # 5. Mehrdeutig?
    if len(good_matches) > 1:
        self.pending_question = {
            'type': 'target',
            'command': command,
            'noun': noun,
            'options': good_matches
        }
        return ConversationResult(
            status='needs_clarification',
            question=self._get_clarification_question(command, noun),
            options=good_matches
        )

    # 6. Eindeutig! → Action bauen
    action = Action(
        command=command,
        targets=[good_matches[0]],
        verb=self.pending_question.get('verb', '') if self.pending_question else '',
        noun=noun
    )
    return ConversationResult(
        status='action_ready',
        action=action
    )
```

---

### Helper im ConversationSystem

```python
def _get_target_question(self, command: str) -> str:
    """Generiert Rückfrage je nach Command"""
    questions = {
        'go': 'Wohin möchtest du gehen?',
        'take': 'Was möchtest du aufheben?',
        'drop': 'Was möchtest du ablegen?',
        'use': 'Was möchtest du benutzen?',
        'examine': 'Was möchtest du untersuchen?'
    }
    return questions.get(command, 'Was genau?')

def _get_clarification_question(self, command: str, noun: str) -> str:
    """Generiert Rückfrage bei Mehrdeutigkeit"""
    if command == 'take':
        return f"Welches '{noun}' meinst du?"
    elif command == 'go':
        return f"Wohin genau?"
    else:
        return f"Was genau meinst du mit '{noun}'?"
```

---

### Helper im Controller

```python
def _get_candidates(self, command: str) -> list:
    """Gibt relevante Entities für Command zurück - IM CONTROLLER!"""
    if command == 'go':
        return self.game_state['exits']
    elif command == 'take':
        return self.game_state['items']
    elif command == 'drop':
        return self.game_state['inventory']
    elif command in ['use', 'examine']:
        return self.game_state['items'] + self.game_state['inventory']
    else:
        return []
```

---

## View-Integration

### Neue Methode: show_question()

```python
class GameView:
    def show_question(self, question: str, options: List[dict]):
        """Zeigt Rückfrage mit nummerierten Optionen"""

        # Frage anzeigen
        self.console.print(f"\n[bold yellow]{question}[/bold yellow]")

        # Optionen nummeriert
        for i, option in enumerate(options, start=1):
            name = option.get('name', option.get('command', '???'))
            description = option.get('description', '')

            if description:
                self.console.print(f"  [cyan][{i}][/cyan] {name} [dim]({description})[/dim]")
            else:
                self.console.print(f"  [cyan][{i}][/cyan] {name}")

        # Hinweis
        self.console.print("[dim]Wähle eine Nummer oder 'abbrechen'[/dim]")
```

**Beispiel-Output:**
```
Welchen Schlüssel meinst du?
  [1] Rostiger Schlüssel (alt und verbeult)
  [2] Goldener Schlüssel (glänzt prächtig)
Wähle eine Nummer oder 'abbrechen'

→
```

---

## Testing-Szenarien

### 1. Happy Path
- ✅ Eindeutiger Command + eindeutiges Target
- **Test:** "gehe zur taverne" → Direkt ausgeführt

### 2. Missing Noun
- ✅ Command klar, aber kein Objekt angegeben
- **Test:** "gehe" → Rückfrage "Wohin?" → User wählt → Ausgeführt

### 3. Ambiguous Command
- ✅ Mehrere Commands über Threshold
- **Test:** "mach feuer" → Rückfrage "use oder examine?" → User wählt → Weiter zu Target

### 4. Ambiguous Target
- ✅ Mehrere Entities ähnlich
- **Test:** "nimm schlüssel" → Rückfrage "Welchen?" → User wählt → Ausgeführt

### 5. No Match
- ✅ Weder Command noch Target gefunden
- **Test:** "tanze" → Error "Ich verstehe 'tanze' nicht."

### 6. Low Confidence
- ✅ Score zu niedrig für Auto-Accept
- **Test:** "gehe zu xyz" → Error "Ich bin mir nicht sicher was 'xyz' sein soll."

### 7. Cancel Mid-Conversation
- ✅ User gibt "abbrechen" während Rückfrage
- **Test:** "gehe" → Rückfrage → User: "abbrechen" → "Abgebrochen." → Zurück zu Normal

### 8. Invalid Choice
- ✅ User gibt ungültige Nummer bei Auswahl
- **Test:** Rückfrage [1] [2] → User: "5" → Error "Bitte wähle 1 oder 2."

---

## Erweiterungsmöglichkeiten (Future)

### 1. Multi-Objekt-Commands
```python
# "benutze schlüssel auf truhe"
Action(
    command='use',
    targets=[
        {'id': 'schluessel', 'name': 'Goldener Schlüssel'},
        {'id': 'truhe', 'name': 'Verschlossene Truhe'}
    ]
)
```

### 2. NPC-Dialoge
```python
# Neuer ConversationType: 'dialog'
pending_question = {
    'type': 'dialog',
    'npc_id': 'wirt',
    'dialog_node': 'greeting',
    'options': [
        {'text': 'Hast du Arbeit?', 'next_node': 'quest_offer'},
        {'text': 'Auf Wiedersehen', 'next_node': 'exit'}
    ]
}
```

### 3. Fuzzy-Matching
```python
# Bei Typos/Tippfehlern
user_input = "ghe zur taverne"  # Typo: "ghe" statt "gehe"
→ Fuzzy-Match findet "gehen" trotzdem (Levenshtein Distance)
```

### 4. Context-Aware Defaults
```python
# Wenn User mehrfach "nimm" sagt ohne Objekt:
"nimm"  # 1. Mal → Rückfrage
User wählt: Schwert
"nimm"  # 2. Mal → Auto-wählt letztes Item (Schwert) als Default
```

---

## Zusammenfassung

### Architektur-Prinzip: Statechart-Ready

**Ein GameState Container mit parallelen Regionen (WorldState + ConversationState):**

```
┌─────────────────────────────────────────────────┐
│                   GameState                      │
│  running: bool                                   │
│  ┌──────────────────┐  ┌─────────────────────┐  │
│  │   WorldState     │  │ ConversationState   │  │
│  │  ─────────────   │  │  ────────────────   │  │
│  │  location        │  │  status: Enum       │  │
│  │  items           │  │  question           │  │
│  │  exits           │  │  options            │  │
│  │  inventory       │  │  message            │  │
│  │                  │  │                     │  │
│  │  update(...)     │  │  ask(question, opt) │  │
│  └──────────────────┘  │  reset()            │  │
│                        │  is_waiting()       │  │
│  start()               └─────────────────────┘  │
│  stop()                                          │
└─────────────────────────────────────────────────┘
```

**Parallele Regionen:** WorldState und ConversationState laufen unabhängig, werden aber zusammen verwaltet.

| Komponente | Verantwortung |
|------------|---------------|
| **Controller** | Orchestriert Flow. Ruft Parser, EmbeddingUtils auf. Manipuliert State. Führt Actions aus. |
| **GameState** | Container-Dataclass mit `running`, `world`, `conversation` |
| **WorldState** | Dataclass: location, items, exits, inventory + `update()` Methode |
| **ConversationState** | Dataclass: status (Enum), question, options, message + `ask()`, `reset()`, `is_waiting()` Methoden |
| **WorldModel** | Neo4j Repository für Datenbank-Queries |
| **SmartParserUtils** | Extrahiert verb/noun aus Text (pure function) |
| **EmbeddingUtils** | Semantic Matching (pure function) |
| **ConversationUtils** | Nur `has_pending_question()` Helper |

### Dataclasses mit Methoden

```python
@dataclass
class GameState:
    running: bool = False
    world: WorldState = field(default_factory=WorldState)
    conversation: ConversationState = field(default_factory=ConversationState)

    def start(self): self.running = True
    def stop(self): self.running = False

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

### Zugriff im Controller

```python
# Ein Container für alles
self.state = GameState()

# Lifecycle
self.state.start()
self.state.stop()

# World aktualisieren
self.state.world.update(
    location=self.model.current_location(),
    items=self.model.location_content(),
    exits=self.model.location_exits(),
    inventory=self.model.player_inventory()
)

# Rückfrage stellen
self.state.conversation.ask("Wohin?", exits)

# Check ob Rückfrage aktiv
if self.state.conversation.is_waiting():
    prompt = "→ "

# Rückfrage zurücksetzen
self.state.conversation.reset()
```

### Dateien

```
src/model/
├── game_state.py           # GameState Container (mit WorldState, ConversationState)
├── world_model.py          # Neo4j Repository

src/utils/
├── conversation_system.py  # ConversationUtils (minimal)
├── smart_parser.py         # SmartParserUtils
└── embedding_utils.py      # EmbeddingUtils
```

### Kernvorteile

- ✅ **Statechart-Ready** - Parallele Regionen vorbereitet
- ✅ **Dataclasses mit Methoden** - Logik gekapselt, nicht im Controller
- ✅ **field(default_factory=...)** - Korrekte mutable Defaults
- ✅ **Controller orchestriert** - Keine Logik in Utils ausgelagert
- ✅ **Status als Enum** - Keine Typos bei Status-Werten
- ✅ **Ein State-Container** - `self.state` statt viele Variablen
- ✅ **Erweiterbar** - Später für NPC-Dialoge, Combat, Quests (neue Regionen)

---

**Version:** 4.0 (Statechart-Ready Architektur)
**Letzte Aktualisierung:** 21. Dezember 2024

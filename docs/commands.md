# Command-Definitionen - RagVenture

Definiert alle erlaubten Commands im Spiel und deren Verarbeitung.

---

## Command-Übersicht

### Bewegung & Navigation

#### `go` (Bewegen)
- **Syntax:** `go <location>` oder `gehe zu <location>`
- **Alias:** gehen, laufen, bewegen, besuchen, kommen
- **Objekt:** Location (Name oder ID)
- **Search Context:** Nur erreichbare Locations (via `ERREICHT` Relationship)
- **Preconditions:**
  - Location ist verbunden
  - Location ist nicht verschlossen (`is_locked=False`)
  - Bei `requires_light=True`: Player hat angezündete Lichtquelle

**Beispiele:**
```
geh zur Taverne
lauf zum Marktplatz
besuche die Schmiede
```

---

### Inventar-Verwaltung

#### `take` (Aufnehmen)
- **Syntax:** `take <item>` oder `nimm <item>`
- **Alias:** nehmen, holen, packen, greifen, schnappen, aufheben
- **Objekt:** Item (Name oder ID)
- **Search Context:** Items an aktueller Location (via `IST_IN`)
- **Preconditions:**
  - Item ist aufhebbar (`is_takeable=True`)
  - Item ist nicht im Inventar

**Beispiele:**
```
nimm den Schlüssel
hol die Fackel
greif nach dem Hammer
```

#### `drop` (Ablegen)
- **Syntax:** `drop <item>` oder `lege <item> ab`
- **Alias:** ablegen, wegwerfen, hinlegen, hinstellen
- **Objekt:** Item (Name oder ID)
- **Search Context:** Player-Inventar (via `TRÄGT`)
- **Preconditions:**
  - Item ist im Inventar

**Beispiele:**
```
lege den Schlüssel ab
leg die Fackel hin
stell das Schwert hin
```

**Hinweis:** Das Inventar ist keine separate Location - Items mit `IST_IN` → Inventar-Location werden als "getragen" betrachtet.

---

### Item-Interaktion

#### `use` (Benutzen)
- **Syntax:** `use <item>` oder `use <item1> on <item2>`
- **Alias:** benutzen, verwenden, anwenden, öffnen, betätigen, probieren, aktivieren
- **Objekt:** 1-2 Items (Name oder ID)
- **Search Context:** Inventar + Location-Items
- **Preconditions:**
  - Item ist benutzbar (`is_usable=True`)
  - Bei 2 Objekten: Relationship zwischen ihnen existiert

**Verarbeitung:**
1. Check ob Relationship existiert: `(item1)-[rel]->(item2)`
2. Relationship-Type bestimmt Aktion:
   - `ÖFFNET` → `is_locked = False` setzen
   - `KANN_ANZÜNDEN` → `is_lit = True` setzen
   - `KANN_BRECHEN` → Item löschen
   - `BELEUCHTET` → (passiv, prüfen bei `go`)

**Beispiele:**
```
benutze Streichhölzer auf Fackel
öffne die Truhe mit dem Schlüssel
verwende den Hammer auf die Truhe
```

#### `examine` (Untersuchen)
- **Syntax:** `examine <object>` oder `untersuche <object>`
- **Alias:** untersuchen, betrachten, ansehen, anschauen, inspizieren, prüfen, mustern
- **Objekt:** Item, NPC oder Location
- **Search Context:** Location-Items + NPCs + aktuelle Location
- **Zeigt:** Detaillierte Beschreibung + Properties

**Beispiele:**
```
untersuche die Truhe
betrachte den Wirt
sieh dir den Hammer an
```

#### `read` (Lesen)
- **Syntax:** `read <item>` oder `lies <item>`
- **Alias:** lesen, durchlesen, vorlesen
- **Objekt:** Item (Name oder ID)
- **Search Context:** Inventar + Location-Items
- **Preconditions:**
  - Item ist lesbar (`is_readable=True`)

**Beispiele:**
```
lies das Buch
les die Gravur
durchlese die Inschrift
```

---

### NPC-Interaktion

#### `talk` (Sprechen)
- **Syntax:** `talk to <npc>` oder `sprich mit <npc>`
- **Alias:** sprechen, reden, unterhalten
- **Objekt:** NPC (Name oder ID)
- **Search Context:** NPCs an aktueller Location
- **Zeigt:** NPC.dialogue (später: LLM-generiert)

**Beispiele:**
```
sprich mit dem Wirt
rede mit dem Händler
unterhalte dich mit dem Schenk
```

#### `trade` (Handeln) - *Future*
- **Syntax:** `trade with <npc>`
- **Preconditions:** `npc.is_trader=True`

---

### Information

#### `look` (Umschauen)
- **Syntax:** `look` oder `look around`
- **Alias:** schauen, umschauen, umsehen
- **Objekt:** Keins
- **Zeigt:**
  - Aktuelle Location (Name, Beschreibung)
  - Items an Location
  - NPCs an Location
  - Verfügbare Ausgänge

**Beispiele:**
```
look
schau dich um
sieh dich um
```

---

### Meta-Commands

#### `help` (Hilfe)
- **Syntax:** `help`
- **Zeigt:** Liste aller Commands

#### `quit` (Beenden)
- **Syntax:** `quit` oder `exit`
- **Beendet:** Spiel

---

## Command-Mapping (Smart Parser)

Der Smart Parser mappt deutsche Verben zu Commands via Embedding-Similarity:

### Verb-Embeddings pro Command

```python
COMMAND_VERBS = {
    'go': [
        'gehen', 'laufen', 'bewegen', 'kommen',
        'marschieren', 'wandern', 'rennen'
    ],
    'take': [
        'nehmen', 'holen', 'packen', 'greifen', 'aufheben',
        'mitnehmen', 'aufsammeln', 'einsammeln'
    ],
    'drop': [
        'ablegen', 'wegwerfen',
        'hinlegen', 'hinstellen'
    ],
    'use': [
        'benutzen', 'verwenden', 'anwenden', 'öffnen',
        'einsetzen', 'nutzen', 'gebrauchen', 'bedienen'
    ],
    'examine': [
        'untersuchen', 'betrachten', 'inspizieren',
        'mustern', 'prüfen', 'begutachten', 'analysieren'
    ],
    'read': [
        'lesen', 'durchlesen', 'vorlesen', 'studieren',
        'entziffern'
    ],
    'talk': [
        'sprechen', 'reden', 'unterhalten',
        'quatschen', 'plaudern', 'kommunizieren'
    ],
    'look': [
        'schauen', 'umschauen', 'umsehen', 'gucken', 'ansehen', 'anschauen',
        'blicken', 'spähen'
    ]
}
```

**Matching:**
- User-Input: "Schnapp dir den Kristall"
- Parser extrahiert Verb: "schnappen"
- Embedding-Similarity zu allen Commands
- Höchster Score: `take` (wegen "schnappen" in Liste)
- Objekt: "Kristall"
- Output: `{'action': 'take', 'objects': ['kristall']}`

---

## Command-Kontext-Awareness

Jeder Command sucht nur in relevanten Bereichen:

| Command | Search Scope | Relationship |
|---------|-------------|--------------|
| `go` | Connected Locations | `(current)-[:ERREICHT]->(target)` |
| `take` | Location Items | `(item)-[:IST_IN]->(current_loc)` |
| `drop` | Player Inventory | `(player)-[:TRÄGT]->(item)` |
| `use` | Inventory + Location | `(player)-[:TRÄGT]->()` + `()-[:IST_IN]->(loc)` |
| `examine` | Items + NPCs + Location | Alle an aktueller Location |
| `read` | Inventory + Location Items | Items die `is_readable=True` haben |
| `talk` | NPCs at Location | `(npc)-[:IST_IN]->(current_loc)` |
| `look` | Current Location | `(player)-[:IST_IN]->(loc)` |

**Hinweis:** `inventory` ist kein eigener Command mehr - das Inventar wird als spezielle Location behandelt.

**Vorteil:** Reduziert Ambiguität

**Beispiel:**
- Location A hat "Goldener Schlüssel"
- Location B hat "Silberner Schlüssel"
- Player ist in A
- `"nimm Schlüssel"` → Sucht nur in A → Findet "Goldener Schlüssel"

---

## Precondition-Checks

Commands haben Vorbedingungen die geprüft werden:

### `take`
```python
def can_take_item(item_id):
    query = """
    MATCH (i:Item {id: $item_id})
    MATCH (p:Player)-[:IST_IN]->(loc:Location)
    MATCH (i)-[:IST_IN]->(loc)  # Muss an aktueller Location sein
    WHERE i.is_takeable = true   # Muss aufhebbar sein
    RETURN i
    """
    result = run_query(query, {'item_id': item_id})
    return len(result) > 0
```

### `go`
```python
def can_move_to_location(location_id):
    query = """
    MATCH (p:Player)-[:IST_IN]->(current:Location)
    MATCH (current)-[:ERREICHT]->(target:Location {id: $location_id})
    WHERE target.is_locked = false  # Nicht verschlossen

    # Falls requires_light=true: Check Lichtquelle
    OPTIONAL MATCH (p)-[:TRÄGT]->(light:Item)
    WHERE light.is_light_source = true AND light.is_lit = true

    WITH target,
         CASE
           WHEN target.requires_light = true
           THEN count(light) > 0
           ELSE true
         END AS has_light

    WHERE has_light = true
    RETURN target
    """
    result = run_query(query, {'location_id': location_id})
    return len(result) > 0
```

### `use`
```python
def can_use_item_on_target(tool_id, target_id):
    query = """
    MATCH (tool {id: $tool_id})-[rel]->(target {id: $target_id})
    RETURN type(rel) AS action_type
    """
    result = run_query(query, {'tool_id': tool_id, 'target_id': target_id})
    return result[0]['action_type'] if result else None
```

---

## Output-Format (Parser → Controller)

Der Parser gibt folgendes Format zurück:

```python
{
    'action': str,        # Command-Name (go, take, use, etc.)
    'targets': [str],     # Liste von Item/Location/NPC IDs
    'raw': str,          # Original-Input (für Debugging)
    'confidence': float   # Optional: Confidence-Score (0.0-1.0)
}
```

**Beispiele:**

Input: `"Nimm den goldenen Schlüssel"`
```python
{
    'action': 'take',
    'targets': ['schluessel'],
    'raw': 'Nimm den goldenen Schlüssel',
    'confidence': 0.85
}
```

Input: `"Benutze Streichhölzer auf Fackel"`
```python
{
    'action': 'use',
    'targets': ['streichhoelzer', 'fackel'],
    'raw': 'Benutze Streichhölzer auf Fackel',
    'confidence': 0.92
}
```

Input: `"Schau dich um"`
```python
{
    'action': 'look',
    'targets': [],
    'raw': 'Schau dich um',
    'confidence': 0.95
}
```

---

## Disambiguation (Rückfragen) mit ConversationSystem

Das **ConversationSystem** stellt automatisch Rückfragen bei Mehrdeutigkeiten oder fehlenden Informationen. Der User antwortet mit nummerierten Auswahlen (1, 2, 3, ...).

---

### Szenario 1: Fehlendes Objekt

**User-Input:** `"gehe"`

**Problem:** Command ist klar ("go"), aber kein Ziel angegeben.

**Flow:**
```
User: "gehe"
  ↓
ConversationSystem: Phase 1 ✅ Command "go" eindeutig
ConversationSystem: Phase 2 ❌ Kein Noun
  ↓
View: "Wohin möchtest du gehen?"
      [1] Mo's Taverne
      [2] Finsterwald
      [3] Schmiede
  ↓
User: "2"
  ↓
ConversationSystem: Phase 2 ✅ Target "Finsterwald" gewählt
  ↓
Execution: move_player('wald')
```

---

### Szenario 2: Mehrdeutige Entities

**User-Input:** `"nimm schlüssel"`

**Problem:** Mehrere Schlüssel vorhanden mit ähnlichem Namen.

**Embedding-Matching:**
```python
matches = [
    {'id': 'rostiger_schluessel', 'name': 'Rostiger Schlüssel', 'score': 0.85},
    {'id': 'goldener_schluessel', 'name': 'Goldener Schlüssel', 'score': 0.83}
]
# Beide über TARGET_SIMILARITY_THRESHOLD (0.70) → Mehrdeutig!
```

**Flow:**
```
User: "nimm schlüssel"
  ↓
ConversationSystem: Phase 1 ✅ Command "take" eindeutig
ConversationSystem: Phase 2 ❌ Mehrere Matches
  ↓
View: "Welchen Schlüssel meinst du?"
      [1] Rostiger Schlüssel (alt und verbeult)
      [2] Goldener Schlüssel (glänzt prächtig)
  ↓
User: "1"
  ↓
ConversationSystem: Phase 2 ✅ Target "Rostiger Schlüssel" gewählt
  ↓
Execution: take_item('rostiger_schluessel')
```

---

### Szenario 3: Mehrdeutige Commands

**User-Input:** `"mach feuer"`

**Problem:** Verb "mach" kann mehrere Commands bedeuten.

**Embedding-Matching:**
```python
command_matches = [
    {'command': 'use', 'sim': 0.96},
    {'command': 'examine', 'sim': 0.95}
]
# Beide über COMMAND_SIMILARITY_THRESHOLD (0.95) → Mehrdeutig!
```

**Flow:**
```
User: "mach feuer"
  ↓
ConversationSystem: Phase 1 ❌ Mehrere Commands
  ↓
View: "Was möchtest du tun?"
      [1] benutzen (use)
      [2] untersuchen (examine)
  ↓
User: "1"
  ↓
ConversationSystem: Phase 1 ✅ Command "use" gewählt
ConversationSystem: Phase 2 → Weiter zu Target-Validierung...
```

---

### Szenario 4: Abbrechen

**User kann jederzeit abbrechen:**

```
User: "gehe"
  ↓
View: "Wohin möchtest du gehen?"
      [1] Taverne
      [2] Wald
  ↓
User: "abbrechen"
  ↓
ConversationSystem: reset()
View: "Abgebrochen."
Prompt: "> " (zurück zu normal)
```

**Abbrechen-Keywords:** `abbrechen`, `zurück`, `cancel`

---

### Validierungs-Schwellwerte

**Command-Matching:**
```python
COMMAND_SIMILARITY_THRESHOLD = 0.95   # Sehr hoch - Commands müssen eindeutig sein
```

**Beispiel:**
```
Input: "gehe"
Matches:
  - 'go': 0.999 ✅ (über Threshold)
  - 'take': 0.87 ❌ (unter Threshold)
→ Eindeutig: "go"
```

**Target-Matching:**
```python
TARGET_SIMILARITY_THRESHOLD = 0.70    # Moderater - erlaubt Flexibilität bei Typos
AMBIGUITY_GAP = 0.05                  # Minimaler Abstand für Eindeutigkeit
```

**Beispiel:**
```
Input: "nimm schlüssel"
Matches:
  - 'goldener_schluessel': 0.87
  - 'silberner_schluessel': 0.85
Gap = 0.02 < AMBIGUITY_GAP (0.05)
→ Mehrdeutig! Rückfrage nötig
```

---

### Multi-Turn Conversations

Das ConversationSystem behält State über mehrere Inputs:

```
User: "nimm"
  ↓
ConversationSystem speichert:
  pending_question = {
      'type': 'target',
      'command': 'take',
      'options': [...]
  }
  ↓
View: "Was möchtest du nehmen?" (Rückfrage)
  ↓
User: "2" (Antwort auf Rückfrage)
  ↓
ConversationSystem resolved pending_question
  → Action ready: take(options[1])
```

**Wichtig:** Prompt ändert sich:
- Normal: `"> "`
- Rückfrage: `"→ "`

---

### Nummerierte Auswahl

**User antwortet mit Zahlen:**
```python
# View zeigt:
[1] Taverne
[2] Wald
[3] Schmiede

# User tippt:
"2"

# Parser:
choice = int(user_input) - 1  # 0-indexed: choice = 1
selected = options[choice]     # options[1] = Wald
```

**Fehlerbehandlung:**
```
User: "5" (aber nur 3 Optionen)
  ↓
View: "Bitte wähle eine Nummer zwischen 1 und 3."
```

---

### Implementation Details

**Siehe:** `docs/conversation_system.md` für vollständige Architektur

**Datenstrukturen:**
```python
@dataclass
class Action:
    command: str           # 'go', 'take', etc.
    targets: List[dict]    # [{'id': '...', 'name': '...'}]
    verb: str             # Original verb (Logging)
    noun: str | None      # Original noun (Logging)

@dataclass
class ConversationResult:
    status: str                    # 'action_ready', 'needs_clarification', 'error'
    action: Action | None          # Bei action_ready
    question: str | None           # Bei needs_clarification
    options: List[dict] | None     # Bei needs_clarification
    message: str | None            # Bei error/cancelled
```

---

## Error-Handling

### Unbekanntes Command
```
Input: "tanze mit dem Wirt"
→ "Ich verstehe den Befehl 'tanze' nicht. Nutze 'help' für eine Liste."
```

### Objekt nicht gefunden
```
Input: "nimm den Diamanten"
→ "Ich kann hier keinen Diamanten finden."
```

### Precondition Failed
```
Input: "geh zum Finsterwald" (ohne Licht)
→ "Es ist zu dunkel! Du brauchst eine Lichtquelle."
```

### Item nicht nutzbar
```
Input: "benutze den Beutel"
→ "Du weißt nicht wie du den Beutel benutzen sollst."
```

---

## Future Commands

Geplant für spätere Phasen:

- `give <item> to <npc>` - Item verschenken
- `trade with <npc>` - Handeln
- `attack <npc> with <weapon>` - Kampf
- `combine <item1> with <item2>` - Crafting
- `wait` - Zeit vergehen lassen
- `save` / `load` - Spielstand speichern

---

**Version:** 1.1 (mit ConversationSystem)
**Letzte Aktualisierung:** 18. Dezember 2024
**Status:** Definition Complete ✅

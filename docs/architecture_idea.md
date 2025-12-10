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

## Die 3 Hauptkomponenten

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

### 3. GAME CONTROLLER (`src/controller/game_controller.py`)

**Aufgabe**: Orchestriert alle Komponenten + Entity-Matching

**Verantwortlichkeiten (ERWEITERT!):**
- ✅ **Parser → Model → View koordinieren**
- ✅ **Entity-Matching** (Text → DB-ID via Similarity-Berechnung)
- ✅ **Entscheidungen treffen** (Confidence zu niedrig? → Nachfragen)
- ✅ **Ablaufsteuerung** (Was tun bei Fehler? Was bei Ambiguität?)
- ❌ **KEINE Business-Logik** (gehört ins Model)

**Merksatz:**
> **Parser versteht Sprache. Controller orchestriert. Model verwaltet Daten und Regeln.**

**Pseudo-Code (NEUE ARCHITEKTUR):**
```python
def process_command(raw_input):
    # 1. Parser: Text → Strukturierte Info (KEIN DB-Zugriff!)
    parsed = self.parser.parse(raw_input)
    # → {'command': 'take', 'object_text': 'Schlüssel', 'adjectives': ['goldenen'], ...}

    # 2. Controller: Prüfe Parser-Confidence
    if parsed['confidence'] < 0.5:
        self.view.show_message("Ich habe dich nicht verstanden.")
        return

    # 3. Controller: Routing basierend auf Command
    if parsed['command'] == 'take':
        # Controller holt ALLE Items vom Model (gecacht!)
        items = self.current_location_cache['items']
        # oder: items = self.model.get_items_at_location()

        # Controller macht Matching (Similarity-Berechnung)
        match = self._find_best_match(
            parsed['object_text'],
            parsed['adjectives'],
            candidates=items
        )
        # → {'item_id': 'schluessel', 'similarity': 0.89}

        # 4. Controller: Entscheidung basierend auf Match-Qualität
        if match is None:
            self.view.show_message(f"Ich sehe hier kein {parsed['object_text']}.")
            return

        if match['similarity'] < 0.5:
            # Zu unsicher → Nachfragen (Ja/Nein-Dialog)
            self.view.show_message(f"Meinst du {match['name']}?")
            # TODO: Dialog-System
            return

        # 5. Controller: Aktion ausführen via Model
        result = self.model.take_item(match['item_id'])

        # 6. Controller: View aktualisieren
        if result:
            self.view.show_message(f"Du nimmst {result['name']}.")
        else:
            self.view.show_message("Das kannst du nicht nehmen.")

    # ... weitere Commands

def _find_best_match(self, object_text, adjectives, candidates):
    """
    Entity-Matching im Controller (nicht im Model!)
    Verwendet Sentence Transformer für Similarity
    """
    search_text = ' '.join(adjectives + [object_text])
    search_embedding = self.sentence_model.encode(search_text)

    best_match = None
    best_similarity = 0.0

    for item in candidates:
        similarity = util.cos_sim(search_embedding, item['embedding'])[0][0].item()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = {'item_id': item['id'], 'name': item['name'], 'similarity': similarity}

    return best_match if best_similarity > 0.3 else None
```

**Faustregel:**
> Alles was mit **Daten und Logik** zu tun hat → **Model**.
> Alles was **Ablauf und UI** betrifft → **Controller**.
> Alles was **Text-Verständnis** betrifft → **Parser**.

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

## Datenfluss-Diagramm

```
User Input
    ↓
[Parser] → ParsedCommand
    ↓
[Controller] → validates & routes
    ↓
[Model] ← → [Neo4j Database]
    ↓
[Controller] ← returns data
    ↓
[View] → Rich Console Output
    ↓
User sees result
```

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

- `smart_parser_architecture.md` - Details zur Smart-Parser-Implementierung (Layer 1-2)
- `architecture_notes_dialog_caching.md` - Konzepte für Dialog-System und Caching-Strategie
- `neo4j_cheatsheet.md` - Cypher-Query-Referenz
- `CLAUDE.md` - Aktuelle Projekt-Instruktionen

---

**Status**: Living Document
**Letzte Aktualisierung**: 4. Dezember 2024
**Version**: MVP Phase 1 + Smart Parser Architecture

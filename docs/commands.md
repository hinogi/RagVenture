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

## Disambiguation (Rückfragen)

Wenn Object-Matching mehrdeutig ist:

**Szenario:** Zwei Items mit ähnlichem Namen
- "Goldener Schlüssel" (Score: 0.87)
- "Silberner Schlüssel" (Score: 0.85)

**Controller-Handling:**
1. Parser gibt beide Matches zurück
2. Controller zeigt Rückfrage:
   ```
   Welchen Schlüssel meinst du?
   [1] Goldener Schlüssel
   [2] Silberner Schlüssel
   ```
3. User wählt: `1`
4. Command wird ausgeführt mit gewähltem Item

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

**Version:** 1.0
**Letzte Aktualisierung:** Dezember 2025
**Status:** Definition Complete ✅

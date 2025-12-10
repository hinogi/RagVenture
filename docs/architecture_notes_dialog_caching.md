# Architektur-Notizen: Dialog-System & Caching

**Status:** Konzept-Phase - Noch nicht implementiert
**Datum:** 4. Dezember 2024

Diese Notizen dokumentieren Überlegungen zu einem Dialog-System und einer Caching-Strategie für bessere Performance und UX.

---

## 1. Dialog-Management-System

### Motivation
- Niedrige Confidence-Scores bei Parser/Matching → User nachfragen
- Mehrere ähnliche Items am Ort → User auswählen lassen
- Bessere UX durch geführte Interaktion

### Konzept: DialogState im Controller

```python
class DialogState:
    """
    Repräsentiert einen aktiven Dialog mit dem User
    """
    def __init__(self, dialog_type, question, options, on_select_callback):
        self.dialog_type = dialog_type  # 'yes_no', 'multiple_choice'
        self.question = question         # "Meinst du X?"
        self.options = options           # Liste von Optionen (Strings oder Dicts)
        self.on_select_callback = on_select_callback  # Callback-Funktion

class GameController:
    def __init__(self):
        # ... existing ...
        self.dialog_state = None  # None = normaler Modus, DialogState = Dialog aktiv
```

### Dialog-Typen

#### Typ 1: Ja/Nein-Bestätigung
```python
# Use-Case: Niedriger Similarity-Score
if match['similarity'] < 0.5:
    def on_confirm(choice):
        if choice == 'yes':
            self._execute_take_item(match['item_id'])
        else:
            self.view.show_message("Ok, abgebrochen.")

    self.dialog_state = DialogState(
        dialog_type='yes_no',
        question=f"Meinst du {match['name']}?",
        options=['Ja', 'Nein'],
        on_select_callback=on_confirm
    )
    self.view.show_dialog(self.dialog_state)

# View zeigt:
# Meinst du Fackel?
# 1. Ja
# 2. Nein
```

**User-Input:**
- Akzeptiert: `ja`, `j`, `yes`, `y`, `1`
- Akzeptiert: `nein`, `n`, `no`, `2`

#### Typ 2: Multiple Choice
```python
# Use-Case: Mehrere Items mit ähnlichem Namen
matches = [
    {'item_id': 'fackel', 'name': 'Fackel', 'similarity': 0.6},
    {'item_id': 'laterne', 'name': 'Laterne', 'similarity': 0.58},
    {'item_id': 'kerze', 'name': 'Kerze', 'similarity': 0.55}
]

def on_select_item(chosen_item):
    self._execute_take_item(chosen_item['item_id'])

self.dialog_state = DialogState(
    dialog_type='multiple_choice',
    question="Was meinst du?",
    options=matches,
    on_select_callback=on_select_item
)

# View zeigt:
# Was meinst du?
# 1. Fackel
# 2. Laterne
# 3. Kerze
```

**User-Input:**
- Akzeptiert: Nummer (1, 2, 3, ...)
- Fehlerbehandlung: "Ungültige Nummer" → Dialog bleibt aktiv

### Dialog-Handling im Controller

```python
def process_command(self, user_input):
    # WICHTIG: Dialog-Handling VOR normalem Parsing!
    if self.dialog_state:
        return self._handle_dialog_response(user_input)

    # ... normale Command-Verarbeitung ...

def _handle_dialog_response(self, user_input):
    """
    Verarbeitet User-Antwort während eines aktiven Dialogs
    """
    if self.dialog_state.dialog_type == 'yes_no':
        if user_input.lower() in ['ja', 'j', 'yes', 'y', '1']:
            self.dialog_state.on_select_callback('yes')
        elif user_input.lower() in ['nein', 'n', 'no', '2']:
            self.dialog_state.on_select_callback('no')
        else:
            self.view.show_message("Bitte 'ja' oder 'nein' eingeben.")
            return  # Dialog bleibt aktiv!

    elif self.dialog_state.dialog_type == 'multiple_choice':
        try:
            choice_idx = int(user_input) - 1
            if 0 <= choice_idx < len(self.dialog_state.options):
                chosen = self.dialog_state.options[choice_idx]
                self.dialog_state.on_select_callback(chosen)
            else:
                self.view.show_message(f"Bitte eine Nummer zwischen 1 und {len(self.dialog_state.options)}.")
                return  # Dialog bleibt aktiv
        except ValueError:
            self.view.show_message("Bitte eine Nummer eingeben.")
            return  # Dialog bleibt aktiv

    # Dialog beenden (erfolgreich)
    self.dialog_state = None
```

### View-Erweiterungen

```python
class GameView:
    def show_dialog(self, dialog_state):
        """
        Zeigt Dialog-Optionen in Rich-formatiertem Style
        """
        console.print(f"\n[yellow]{dialog_state.question}[/yellow]")

        if dialog_state.dialog_type == 'yes_no':
            console.print("[cyan]1.[/cyan] Ja")
            console.print("[cyan]2.[/cyan] Nein")

        elif dialog_state.dialog_type == 'multiple_choice':
            for idx, option in enumerate(dialog_state.options, 1):
                # option kann String oder Dict sein
                if isinstance(option, dict):
                    display_text = option.get('name', str(option))
                else:
                    display_text = option
                console.print(f"[cyan]{idx}.[/cyan] {display_text}")
```

---

## 2. Caching-Strategie: Location-Cache

### Motivation
- **Problem:** Jedes Item-Matching macht eine DB-Query
- **Lösung:** Alle Entities beim Raum-Betreten einmal laden → Cache
- **Vorteil:** Matching in-memory (sehr schnell), weniger DB-Load

### Location-Cache-Struktur

```python
class GameController:
    def __init__(self):
        # ... existing ...
        self.current_location_cache = {
            'location_id': None,
            'location_name': None,
            'items': [],      # Alle Items am Ort (mit Embeddings!)
            'npcs': [],       # Alle NPCs am Ort
            'exits': []       # Alle Ausgänge (Richtung + Ziel-Location)
        }
```

**items-Struktur:**
```python
[
    {
        'id': 'fackel',
        'name': 'Fackel',
        'description': 'Eine brennende Fackel...',
        'embedding': [0.1, 0.2, 0.3, ...]  # numpy array oder Liste
    },
    {
        'id': 'schluessel',
        'name': 'Goldener Schlüssel',
        'description': 'Ein golden glänzender...',
        'embedding': [...]
    }
]
```

### Cache-Refresh-Logik

```python
def _refresh_location_cache(self):
    """
    Lädt alle Entities der aktuellen Location in den Cache

    Wird aufgerufen bei:
    - Spielstart (run_game)
    - Nach 'visit' (Raum wechseln)
    - Nach 'take' (Item verschwindet vom Ort)
    - Nach 'drop' (Item erscheint am Ort)
    """
    current_loc = self.model.get_current_location()

    self.current_location_cache = {
        'location_id': current_loc['id'],
        'location_name': current_loc['name'],
        'items': self.model.get_items_at_location(current_loc['id']),
        'npcs': self.model.get_npcs_at_location(current_loc['id']),
        'exits': self.model.get_exits(current_loc['id'])
    }

def run_game(self):
    self.running = True
    self.view.show_welcome()

    # WICHTIG: Cache beim Start laden!
    self._refresh_location_cache()

    while self.running:
        command = self.view.get_command()
        self.process_command(command)

def process_command(self, user_input):
    # ... Dialog-Handling ...

    parsed = self.parser.parse(user_input)

    if parsed['command'] == 'take':
        # Verwende Cache statt DB-Query!
        match = self._find_best_match_in_cache(
            parsed['object_text'],
            parsed['adjectives'],
            candidates=self.current_location_cache['items']
        )

        if match:
            result = self.model.take_item(match['item_id'])
            if result:
                # WICHTIG: Cache aktualisieren!
                self._refresh_location_cache()
                self.view.show_message(f"Du nimmst {result['name']}.")
        else:
            self.view.show_message(f"Ich sehe hier kein {parsed['object_text']}.")

    elif parsed['command'] == 'visit':
        # ... Location-Matching ...
        result = self.model.move_player(target_location_id)
        if result:
            # WICHTIG: Cache neu laden (neuer Raum!)
            self._refresh_location_cache()
            self.view.show_location_info(self.current_location_cache)

    elif parsed['command'] == 'drop':
        # ... Item aus Inventar droppen ...
        result = self.model.drop_item(item_id)
        if result:
            # Cache aktualisieren (Item jetzt am Ort)
            self._refresh_location_cache()
```

### Matching-Logik im Controller (statt Model!)

**WICHTIGE ARCHITEKTUR-ÄNDERUNG:**
- Matching wandert vom **Model** in den **Controller**
- Model liefert nur noch komplette Listen
- Controller macht Similarity-Berechnung mit gecachten Entities

```python
class GameController:
    def __init__(self):
        # ... existing ...
        # Sentence Transformer für Matching (nicht nur im Parser!)
        from sentence_transformers import SentenceTransformer, util
        self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def _find_best_match_in_cache(self, object_text, adjectives, candidates):
        """
        Findet bestes Item-Match in gecachten Candidates

        KEIN DB-Zugriff! Arbeitet nur mit candidates-Liste

        Args:
            object_text: "Schlüssel"
            adjectives: ["goldenen"]
            candidates: self.current_location_cache['items']

        Returns:
            dict: {
                'item_id': 'schluessel',
                'name': 'Goldener Schlüssel',
                'similarity': 0.89
            }
            oder None
        """
        if not candidates:
            return None

        # Text kombinieren: "goldenen Schlüssel"
        search_text = ' '.join(adjectives + [object_text])
        search_embedding = self.sentence_model.encode(search_text)

        best_match = None
        best_similarity = 0.0

        for item in candidates:
            # Cosine Similarity
            similarity = util.cos_sim(search_embedding, item['embedding'])[0][0].item()

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'item_id': item['id'],
                    'name': item['name'],
                    'similarity': similarity
                }

        # Schwellwert: Mindestens 0.3 Similarity
        if best_similarity < 0.3:
            return None

        return best_match
```

### Model-Änderungen: Vereinfachung!

**Model gibt jetzt komplette Listen zurück, KEIN Matching mehr:**

```python
class GameModel:
    def get_items_at_location(self, location_id=None):
        """
        Gibt ALLE Items an der Location zurück (mit Embeddings)

        Args:
            location_id: Optional - wenn None, aktuelle Location vom Player

        Returns:
            list: [
                {
                    'id': 'fackel',
                    'name': 'Fackel',
                    'description': '...',
                    'embedding': [0.1, 0.2, ...]
                },
                ...
            ]
        """
        if location_id is None:
            query = """
                MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
                MATCH (i:Item)-[:IST_IN]->(loc)
                RETURN i.id as id, i.name as name,
                       i.description as description,
                       i.name_embedding as embedding
            """
        else:
            query = """
                MATCH (i:Item)-[:IST_IN]->(loc:Location {id: $loc_id})
                RETURN i.id as id, i.name as name,
                       i.description as description,
                       i.name_embedding as embedding
            """

        return self._run_query(query, {'loc_id': location_id} if location_id else {})

    def get_inventory_items(self):
        """
        Gibt ALLE Items im Inventar zurück (mit Embeddings)
        """
        query = """
            MATCH (p:Player {id: 'player'})-[:TRÄGT]->(i:Item)
            RETURN i.id as id, i.name as name,
                   i.description as description,
                   i.name_embedding as embedding
        """
        return self._run_query(query)

    def get_npcs_at_location(self, location_id=None):
        """
        Gibt ALLE NPCs an der Location zurück
        """
        # Ähnliche Logik wie get_items_at_location
        pass

    def get_exits(self, location_id=None):
        """
        Gibt alle Ausgänge zurück
        """
        # ERREICHT-Relationships abfragen
        pass

    # ENTFERNT: find_matching_item() - nicht mehr nötig!
    # Matching passiert im Controller mit Cache
```

**Model-Verantwortlichkeiten (vereinfacht):**
- ✅ DB-Queries ausführen (komplette Listen zurückgeben)
- ✅ Aktionen ausführen (take_item, drop_item, move_player)
- ✅ Business-Validierung (ist Item nehmbar? ist Location erreichbar?)
- ❌ **KEIN Matching mehr** (wandert in Controller)

---

## 3. Erweiterte Dialog-Szenarien

### Szenario 1: Niedriger Command-Confidence
```python
parsed = self.parser.parse("Hmm was?")
# → {'command': 'unknown', 'confidence': 0.3, ...}

if parsed['confidence'] < 0.5:
    self.view.show_message("Ich habe dich nicht verstanden. Versuche es anders.")
    return
```

### Szenario 2: Niedriger Item-Similarity
```python
match = self._find_best_match_in_cache("Lampe", [], items)
# → {'item_id': 'fackel', 'name': 'Fackel', 'similarity': 0.45}

if match['similarity'] < 0.5:
    # Ja/Nein-Dialog
    # ... (siehe oben)
```

### Szenario 3: Mehrere ähnliche Matches
```python
# IDEE: _find_best_match_in_cache könnte ALLE guten Matches zurückgeben

def _find_all_good_matches(self, object_text, adjectives, candidates, threshold=0.4):
    """
    Gibt ALLE Matches über threshold zurück (sortiert nach Similarity)
    """
    search_text = ' '.join(adjectives + [object_text])
    search_embedding = self.sentence_model.encode(search_text)

    matches = []
    for item in candidates:
        similarity = util.cos_sim(search_embedding, item['embedding'])[0][0].item()
        if similarity >= threshold:
            matches.append({
                'item_id': item['id'],
                'name': item['name'],
                'similarity': similarity
            })

    # Sortieren nach Similarity (absteigend)
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches

# Im Controller:
matches = self._find_all_good_matches("Licht", [], items, threshold=0.4)

if len(matches) == 0:
    self.view.show_message("Das sehe ich hier nicht.")
elif len(matches) == 1:
    # Eindeutig → direkt nehmen (wenn Similarity hoch genug)
    if matches[0]['similarity'] > 0.7:
        self._execute_take_item(matches[0]['item_id'])
    else:
        # Ja/Nein-Dialog
        pass
else:
    # Mehrere Matches → Multiple Choice
    def on_select(chosen):
        self._execute_take_item(chosen['item_id'])

    self.dialog_state = DialogState(
        dialog_type='multiple_choice',
        question="Was meinst du?",
        options=matches,
        on_select_callback=on_select
    )
    self.view.show_dialog(self.dialog_state)
```

---

## 4. Performance-Überlegungen

### Vorteile der Caching-Strategie

**Ohne Cache:**
- `take fackel` → DB-Query (get all items) → Matching → take_item
- `take schlüssel` → DB-Query (get all items) → Matching → take_item
- `take kerze` → DB-Query (get all items) → Matching → take_item
- **3 DB-Queries** für 3 Commands

**Mit Cache:**
- `visit taverne` → DB-Query (get all items/npcs/exits) → **Cache gefüllt**
- `take fackel` → **Cache-Lookup** → Matching → take_item → **Cache-Refresh**
- `take schlüssel` → **Cache-Lookup** → Matching → take_item → **Cache-Refresh**
- **3 DB-Queries** (1x initial, 2x refresh)

**Aber:** Bei vielen takes im selben Raum sind Refreshes teuer. Alternative:

### Optimierung: Selektives Cache-Update

```python
def process_command(self, user_input):
    # ...
    if parsed['command'] == 'take':
        match = self._find_best_match_in_cache(...)
        if match:
            result = self.model.take_item(match['item_id'])
            if result:
                # OPTIMIERUNG: Item nur aus Cache entfernen (kein Full-Refresh)
                self._remove_item_from_cache(match['item_id'])
                self.view.show_message(f"Du nimmst {result['name']}.")

def _remove_item_from_cache(self, item_id):
    """
    Entfernt Item aus Cache ohne DB-Query
    """
    self.current_location_cache['items'] = [
        item for item in self.current_location_cache['items']
        if item['id'] != item_id
    ]

def _add_item_to_cache(self, item_dict):
    """
    Fügt Item zum Cache hinzu (nach 'drop')
    Braucht aber Embedding → DB-Query nötig, oder Item-Dict aus Inventory-Cache
    """
    self.current_location_cache['items'].append(item_dict)
```

**Problem bei _add_item_to_cache:**
- Item braucht Embedding für Matching
- Entweder: Full-Refresh (sicher, aber DB-Query)
- Oder: Item-Dict aus Inventory-Cache übernehmen (wenn vorhanden)

**Empfehlung:** Erstmal Full-Refresh (einfach), später optimieren wenn nötig.

### Memory-Overhead

**Pro Location:**
- ~5-10 Items × ~400 floats (Embedding) = ~16-32 KB
- ~3-5 NPCs × Embedding + Daten = ~10-20 KB
- Exits, Location-Info = ~1 KB
- **Gesamt: ~30-50 KB pro Location**

**Kein Problem** - selbst bei 100 Locations nur ~5 MB RAM.

---

## 5. Zusammenfassung: Neue Verantwortlichkeiten

### Parser (unverändert)
- ✅ NLP (SpaCy)
- ✅ Verb → Command Matching (Sentence Transformer)
- ✅ Output: `{'command': ..., 'object_text': ..., 'adjectives': ...}`

### Controller (erweitert!)
- ✅ Dialog-State-Management (`DialogState`)
- ✅ Location-Cache (Items, NPCs, Exits)
- ✅ **Matching-Logik** (Similarity-Berechnung mit gecachten Entities)
- ✅ Entscheidungen (Confidence-Thresholds, Multiple Choice)
- ✅ Parser → Model → View Orchestrierung

### Model (vereinfacht!)
- ✅ DB-Queries (gibt **komplette Listen** zurück, nicht einzelne Matches)
- ✅ Aktionen ausführen (take_item, drop_item, move_player)
- ✅ Business-Validierung (ist Aktion erlaubt?)
- ❌ **KEIN Matching mehr** (wandert in Controller)

### View (erweitert)
- ✅ show_dialog() für Ja/Nein und Multiple Choice
- ✅ Bestehende Methoden unverändert

---

## 6. Offene Fragen

### Frage 1: Inventory auch cachen?
- **Problem:** Bei `drop` muss Item-Embedding bekannt sein für Location-Cache
- **Lösung:** Inventory-Cache parallel führen
- **Vorteil:** `show inventory` ist instant (kein DB-Query)

```python
self.inventory_cache = []  # Analog zu location_cache['items']
```

### Frage 2: Cache-Invalidierung
- **Wann:** Bei Commands die Welt ändern (take, drop, use?, talk?)
- **Wie:** Full-Refresh oder selektiv?
- **Trade-off:** Einfachheit vs. Performance

### Frage 3: Dialog-Abbruch?
- User tippt während Dialog etwas anderes (z.B. `quit`)
- **Lösung:** `quit` als Spezialfall erlauben, andere Commands → "Bitte erst Dialog beenden"

```python
def _handle_dialog_response(self, user_input):
    # Spezialfall: quit immer erlauben
    if user_input.lower() == 'quit':
        self.dialog_state = None
        self.running = False
        self.view.show_message("Tschüss!")
        return

    # ... normale Dialog-Verarbeitung ...
```

### Frage 4: NPC-Konversationen?
- Dialog-System auch für NPCs nutzen?
- **Idee:** `talk npc_name` → DialogState mit NPC-Antworten
- **Später:** LLM-Integration für dynamische Dialoge
- **Jetzt:** Statische Antwort-Bäume aus DB

---

## Nächste Schritte

1. Dialog-System prototypen (Ja/Nein erst)
2. Cache-Strategie testen (Performance messen)
3. Matching-Logik in Controller verschieben
4. Model vereinfachen (find_matching_item entfernen)
5. View-Dialog-Methoden implementieren
6. NPC-Konversations-System konzipieren (siehe nächstes Dokument)

---

**Ende der Notizen - Bereit für NPC-Konversations-Konzept**

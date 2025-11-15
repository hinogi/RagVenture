# Neo4j & Cypher Cheat Sheet

Schnellreferenz für Neo4j Graph-Datenbank und Cypher Query Language.

---

## 📦 Neo4j Basics

### Container Management

```bash
# Neo4j Container starten (aus README)
docker run -d \
    --name textadventure-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j_data:/data \
    neo4j:latest

# Container stoppen/starten
docker stop textadventure-neo4j
docker start textadventure-neo4j

# Container löschen (Achtung: Daten bleiben in Volume!)
docker rm textadventure-neo4j

# Volume löschen (Alle Daten weg!)
docker volume rm neo4j_data

# Logs anschauen
docker logs textadventure-neo4j
```

### Zugriff

- **Browser UI**: http://localhost:7474
- **Bolt Protocol**: bolt://localhost:7687
- **Login**: `neo4j` / `password`

---

## 🏗️ Schema Setup

### Constraints (Eindeutigkeit sicherstellen)

```cypher
// Eindeutige IDs für alle Node-Typen
CREATE CONSTRAINT room_id IF NOT EXISTS
FOR (r:Room) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT item_id IF NOT EXISTS
FOR (i:Item) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT npc_id IF NOT EXISTS
FOR (n:NPC) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT player_id IF NOT EXISTS
FOR (p:Player) REQUIRE p.id IS UNIQUE;
```

### Indexes (Performance)

```cypher
// Schnellere Suche nach Namen
CREATE INDEX room_name IF NOT EXISTS
FOR (r:Room) ON (r.name);

CREATE INDEX item_name IF NOT EXISTS
FOR (i:Item) ON (i.name);

CREATE INDEX npc_name IF NOT EXISTS
FOR (n:NPC) ON (n.name);
```

### Schema anzeigen

```cypher
// Alle Constraints
SHOW CONSTRAINTS

// Alle Indexes
SHOW INDEXES

// Datenbank-Statistik
CALL db.schema.visualization()
```

---

## 🎮 Daten erstellen - CREATE

### Nodes erstellen

```cypher
// Einzelne Node
CREATE (r:Room {
  id: "thronsaal",
  name: "Thronsaal",
  description: "Ein prächtiger Raum mit goldenen Säulen."
})

// Mehrere Nodes
CREATE
  (throne:Room {id: "thronsaal", name: "Thronsaal", description: "..."}),
  (dungeon:Room {id: "kerker", name: "Kerker", description: "..."}),
  (key:Item {id: "schluessel", name: "Rostiger Schlüssel"}),
  (guard:NPC {id: "waechter", name: "Wächter"})
```

### Relationships erstellen

```cypher
// Räume verbinden (bidirektional)
MATCH (a:Room {id: "thronsaal"})
MATCH (b:Room {id: "kerker"})
CREATE (a)-[:CONNECTED_TO {direction: "norden"}]->(b)
CREATE (b)-[:CONNECTED_TO {direction: "süden"}]->(a)

// Item in Raum platzieren
MATCH (r:Room {id: "thronsaal"})
MATCH (i:Item {id: "schwert"})
CREATE (r)-[:CONTAINS]->(i)

// Player positionieren
MATCH (p:Player {id: "player1"})
MATCH (r:Room {id: "thronsaal"})
CREATE (p)-[:LOCATED_IN]->(r)
```

### Alles in einem Statement

```cypher
CREATE
  (a:Room {id: "thronsaal", name: "Thronsaal"}),
  (b:Room {id: "kerker", name: "Kerker"}),
  (key:Item {id: "schluessel", name: "Schlüssel"}),
  (player:Player {id: "player1", name: "Held"}),

  (a)-[:CONNECTED_TO {direction: "norden"}]->(b),
  (b)-[:CONNECTED_TO {direction: "süden"}]->(a),
  (b)-[:CONTAINS]->(key),
  (player)-[:LOCATED_IN]->(a)
```

---

## 🔍 Daten abfragen - MATCH

### Einfache Queries

```cypher
// Alle Räume
MATCH (r:Room)
RETURN r

// Raum nach ID
MATCH (r:Room {id: "thronsaal"})
RETURN r

// Nur bestimmte Properties
MATCH (r:Room {id: "thronsaal"})
RETURN r.name, r.description

// Mit WHERE-Filter
MATCH (r:Room)
WHERE r.name CONTAINS "Kammer"
RETURN r
```

### Relationships abfragen

```cypher
// Alle Ausgänge eines Raums
MATCH (current:Room {id: "thronsaal"})-[conn:CONNECTED_TO]->(neighbor:Room)
RETURN neighbor.name, conn.direction

// Items in einem Raum
MATCH (r:Room {id: "thronsaal"})-[:CONTAINS]->(i:Item)
RETURN i.name, i.description

// Player-Position
MATCH (p:Player {id: "player1"})-[:LOCATED_IN]->(r:Room)
RETURN r.id, r.name

// Player-Inventar
MATCH (p:Player {id: "player1"})-[:CARRIES]->(i:Item)
RETURN collect(i.name) as inventory
```

### Komplexe Queries

```cypher
// Raum mit allen Details (Ausgänge + Items)
MATCH (r:Room {id: "thronsaal"})
OPTIONAL MATCH (r)-[conn:CONNECTED_TO]->(neighbor:Room)
OPTIONAL MATCH (r)-[:CONTAINS]->(item:Item)
RETURN
  r.name,
  r.description,
  collect(DISTINCT {direction: conn.direction, room: neighbor.name}) as exits,
  collect(DISTINCT item.name) as items

// Alle NPCs mit ihren Räumen
MATCH (npc:NPC)-[:LOCATED_IN]->(r:Room)
RETURN npc.name, r.name as location
```

---

## ✏️ Daten ändern - SET / DELETE

### Properties ändern

```cypher
// Property setzen
MATCH (npc:NPC {id: "waechter"})
SET npc.mood = "angry"

// Property erhöhen/verringern
MATCH (p:Player {id: "player1"})
SET p.health = p.health - 10

// Mehrere Properties
MATCH (r:Room {id: "kerker"})
SET r.visited = true, r.light_level = "dark"
```

### Daten löschen

```cypher
// Nur Relationship löschen
MATCH (r:Room)-[rel:CONTAINS]->(i:Item {id: "trash"})
DELETE rel

// Node + alle Relationships
MATCH (i:Item {id: "trash"})
DETACH DELETE i

// Alles löschen (VORSICHT!)
MATCH (n)
DETACH DELETE n
```

---

## 🎯 Game-spezifische Patterns

### Player bewegen

```cypher
// Player zu neuem Raum bewegen
MATCH (p:Player {id: $player_id})-[old:LOCATED_IN]->(:Room)
MATCH (current:Room)<-[:LOCATED_IN]-(p)
MATCH (current)-[:CONNECTED_TO {direction: $direction}]->(next:Room)
DELETE old
CREATE (p)-[:LOCATED_IN]->(next)
RETURN next.id, next.name, next.description
```

### Item aufnehmen

```cypher
// Item von Raum zu Player
MATCH (p:Player {id: $player_id})-[:LOCATED_IN]->(r:Room)
MATCH (r)-[rel:CONTAINS]->(item:Item {id: $item_id})
DELETE rel
CREATE (p)-[:CARRIES]->(item)
RETURN item.name + " aufgenommen!"
```

### Item ablegen

```cypher
// Item von Player zu Raum
MATCH (p:Player {id: $player_id})-[rel:CARRIES]->(item:Item {id: $item_id})
MATCH (p)-[:LOCATED_IN]->(r:Room)
DELETE rel
CREATE (r)-[:CONTAINS]->(item)
RETURN item.name + " abgelegt!"
```

### Raum-Info mit allem

```cypher
// Komplette Raum-Info für UI
MATCH (p:Player {id: $player_id})-[:LOCATED_IN]->(r:Room)
OPTIONAL MATCH (r)-[conn:CONNECTED_TO]->(neighbor:Room)
OPTIONAL MATCH (r)-[:CONTAINS]->(item:Item)
OPTIONAL MATCH (npc:NPC)-[:LOCATED_IN]->(r)
RETURN
  r.id,
  r.name,
  r.description,
  collect(DISTINCT {direction: conn.direction, room: neighbor.name}) as exits,
  collect(DISTINCT item.name) as items,
  collect(DISTINCT npc.name) as npcs
```

### Quest-System

```cypher
// NPC will Item haben
MATCH (npc:NPC {id: "waechter"})
MATCH (item:Item {id: "schluessel"})
CREATE (npc)-[:WANTS]->(item)

// NPC gibt Belohnung
MATCH (npc:NPC {id: "waechter"})
MATCH (reward:Item {id: "gold"})
CREATE (npc)-[:GIVES]->(reward)

// Quest-Check
MATCH (p:Player {id: $player_id})-[:CARRIES]->(item:Item)
MATCH (npc:NPC {id: $npc_id})-[:WANTS]->(wanted:Item)
WHERE item.id = wanted.id
RETURN "Quest erfüllbar!" as status
```

---

## 🐍 Python Integration

### Connection Setup

```python
from neo4j import GraphDatabase

class GameDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Nutzen
db = GameDB("bolt://localhost:7687", "neo4j", "password")
```

### Beispiel-Queries in Python

```python
class GameDB:
    # ... (init von oben)

    def get_current_room(self, player_id):
        query = """
        MATCH (p:Player {id: $player_id})-[:LOCATED_IN]->(r:Room)
        OPTIONAL MATCH (r)-[conn:CONNECTED_TO]->(neighbor:Room)
        OPTIONAL MATCH (r)-[:CONTAINS]->(item:Item)
        RETURN
            r.id as id,
            r.name as name,
            r.description as description,
            collect(DISTINCT {direction: conn.direction, room: neighbor.name}) as exits,
            collect(DISTINCT item.name) as items
        """
        result = self.execute_query(query, {"player_id": player_id})
        return result[0] if result else None

    def move_player(self, player_id, direction):
        query = """
        MATCH (p:Player {id: $player_id})-[old:LOCATED_IN]->(current:Room)
        MATCH (current)-[:CONNECTED_TO {direction: $direction}]->(next:Room)
        DELETE old
        CREATE (p)-[:LOCATED_IN]->(next)
        RETURN next.id, next.name
        """
        result = self.execute_query(query, {
            "player_id": player_id,
            "direction": direction
        })
        return result[0] if result else None

    def get_inventory(self, player_id):
        query = """
        MATCH (p:Player {id: $player_id})-[:CARRIES]->(i:Item)
        RETURN collect(i.name) as items
        """
        result = self.execute_query(query, {"player_id": player_id})
        return result[0]['items'] if result else []
```

---

## 🛠️ Nützliche Commands

### Datenbank aufräumen

```cypher
// Alles löschen
MATCH (n) DETACH DELETE n

// Nur Test-Daten
MATCH (n) WHERE n.test = true DETACH DELETE n

// Nur bestimmte Labels
MATCH (i:Item) DETACH DELETE i
```

### Debugging

```cypher
// Anzahl Nodes pro Label
MATCH (n)
RETURN labels(n) as label, count(*) as count

// Alle Relationship-Typen
MATCH ()-[r]->()
RETURN DISTINCT type(r)

// Nodes ohne Relationships
MATCH (n)
WHERE NOT (n)--()
RETURN n

// Orphaned Items (nicht in Raum/Inventar)
MATCH (i:Item)
WHERE NOT (i)<-[:CONTAINS|CARRIES]-()
RETURN i
```

### Performance

```cypher
// Query-Plan anzeigen (Optimierung)
EXPLAIN
MATCH (r:Room {id: "thronsaal"})
RETURN r

// Query tatsächlich ausführen + Stats
PROFILE
MATCH (r:Room {id: "thronsaal"})
RETURN r
```

---

## 📚 Wichtige Cypher-Patterns

```cypher
// MERGE = Upsert (Create or Match)
MERGE (p:Player {id: "player1"})
ON CREATE SET p.created_at = timestamp()
ON MATCH SET p.last_login = timestamp()

// OPTIONAL MATCH = Auch wenn nichts gefunden
MATCH (r:Room)
OPTIONAL MATCH (r)-[:CONTAINS]->(i:Item)
RETURN r, i

// collect() = Ergebnisse sammeln
MATCH (r:Room)-[:CONTAINS]->(i:Item)
RETURN r.name, collect(i.name) as items

// WITH = Intermediate Results
MATCH (p:Player)-[:CARRIES]->(i:Item)
WITH p, count(i) as item_count
WHERE item_count > 5
RETURN p.name, item_count

// CASE = Bedingungen
MATCH (p:Player)
RETURN p.name,
  CASE
    WHEN p.health > 80 THEN "healthy"
    WHEN p.health > 30 THEN "wounded"
    ELSE "critical"
  END as status
```

---

## 🚀 Quick Start: 2-Raum Demo

```cypher
// 1. Schema
CREATE CONSTRAINT room_id IF NOT EXISTS FOR (r:Room) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT player_id IF NOT EXISTS FOR (p:Player) REQUIRE p.id IS UNIQUE;

// 2. Welt erstellen
CREATE
  (start:Room {
    id: "start",
    name: "Startpunkt",
    description: "Du stehst an einem Kreuzweg."
  }),
  (forest:Room {
    id: "forest",
    name: "Dunkler Wald",
    description: "Hohe Bäume umgeben dich."
  }),
  (player:Player {id: "hero", name: "Held", health: 100}),

  (start)-[:CONNECTED_TO {direction: "norden"}]->(forest),
  (forest)-[:CONNECTED_TO {direction: "süden"}]->(start),
  (player)-[:LOCATED_IN]->(start);

// 3. Testen
MATCH (p:Player)-[:LOCATED_IN]->(r:Room)
RETURN r.name as "Aktueller Raum";

// 4. Bewegen
MATCH (p:Player)-[old:LOCATED_IN]->(:Room)
MATCH (current:Room)<-[:LOCATED_IN]-(p)
MATCH (current)-[:CONNECTED_TO {direction: "norden"}]->(next:Room)
DELETE old
CREATE (p)-[:LOCATED_IN]->(next)
RETURN next.name as "Neuer Raum";
```

---

**Pro-Tipp**: Browser UI (http://localhost:7474) hat Auto-Complete für Cypher! Nutze Ctrl+Space für Vorschläge.

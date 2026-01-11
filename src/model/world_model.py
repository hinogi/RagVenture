"""
Neo4j Game Model - DB-Zugriff für Spielwelt.

Wrapper für Neo4j Cypher Queries. Verwaltet Connection und
bietet typsichere Methoden für Location/Item/Inventory Queries.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


class GameModel:
    """
    Model-Komponente im MVC-Pattern.

    Kapselt alle Neo4j DB-Zugriffe. Single Source of Truth für
    Spielwelt-State (Locations, Items, Inventory, Relationships).
    """
    def __init__(self):
        # .env laden
        load_dotenv()

        # DB driver erstellen
        self.driver = GraphDatabase.driver(
            uri=os.getenv('NEO4J_URI'),
            auth=(
                os.getenv('NEO4J_USER'),
                os.getenv('NEO4J_PASSWORD')
            ),
            # notifications_min_severity='OFF'
        )

    def close(self):
        """Schließt Neo4j Driver Connection sauber."""
        self.driver.close()

    def _run_query(self, query, params=None):
        """
        führt eine einzelne Query aus

        args:
            query (str): cypher query
            params (dict): queryparameter

        returns:
            list: liste von dicts mit den ergebnissen
        """
        with self.driver.session() as session:

            result = session.run(query, params or {})
            return [record.data() for record in result]

    def current_location(self):
        """
        Gibt aktuelle Player-Location zurück.

        Returns:
            list[dict]: Location mit id, name, description, name_emb
        """
        query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(location:Location)
        RETURN 
            location.id AS id, 
            location.name AS name, 
            location.description AS description,
            location.name_emb AS name_emb
        """
        return self._run_query(query)

    def location_items(self):
        """
        Gibt Items an aktueller Location zurück.

        Returns:
            list[dict]: Items mit id, name, description, name_emb
        """
        query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
        MATCH (item)-[:IST_IN]->(loc)
        WHERE item <> p
        RETURN 
            item.id AS id, 
            item.name AS name, 
            item.description AS description,
            item.name_emb AS name_emb
        """
        return self._run_query(query)

    def location_exits(self):
        """
        Gibt erreichbare Locations (Exits) zurück.

        Returns:
            list[dict]: Locations mit id, name, description, name_emb
        """
        query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(location:Location)
        MATCH (location)-[:ERREICHT]->(exit:Location)
        RETURN
            exit.id AS id, 
            exit.name AS name, 
            exit.description AS description,
            exit.name_emb AS name_emb
        """
        return self._run_query(query)

    def player_inventory(self):
        """
        Gibt Items im Player-Inventar zurück.

        Returns:
            list[dict]: Items mit id, name, name_emb
        """
        query = """
        MATCH (p:Player {id: 'player'})-[:TRÄGT]->(inventory:Item)
        RETURN 
            inventory.id AS id,
            inventory.name AS name,
            inventory.name_emb AS name_emb
        """
        return self._run_query(query)

    def move_player(self, to_location):
        """
        Bewegt Player zu neuer Location.

        Args:
            to_location (str): Target Location ID

        Returns:
            list[dict]: Neue Location mit id, name, description oder [] bei Fehler
        """
        query = """
        MATCH (p:Player {id: 'player'})-[old:IST_IN]->(current:Location)
        MATCH (current)-[:ERREICHT]->(target:Location {id: $to_location})
        DELETE old
        CREATE (p)-[:IST_IN]->(target)
        RETURN
            target.id AS id, 
            target.name AS name, 
            target.description AS description
        """
        params = {'to_location': to_location}
        return self._run_query(query, params=params)

    def take_item(self, item):
        """
        Nimmt Item von Location in Inventar auf.

        Args:
            item (str): Item ID

        Returns:
            list[dict]: Item mit name oder [] bei Fehler
        """
        query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(loc:Location)
        MATCH (i:Item {id: $item})-[old:IST_IN]->(loc)
        DELETE old
        CREATE (p)-[:TRÄGT]->(i)
        RETURN i.name AS name
        """

        params = {'item': item}
        return self._run_query(query, params=params)

    def drop_item(self, item):
        """
        Legt Item aus Inventar an aktueller Location ab.

        Args:
            item (str): Item ID

        Returns:
            list[dict]: Item mit name oder [] bei Fehler
        """
        query = """
        MATCH (p:Player {id: 'player'})-[old:TRÄGT]->(i:Item {id: $item})
        MATCH (p)-[:IST_IN]->(loc:Location)
        DELETE old
        CREATE (i)-[:IST_IN]->(loc)
        RETURN i.name AS name
        """

        params = {'item': item}
        return self._run_query(query, params=params)

    def use_item(self, item, target):
        """
        Benutzt Item auf Target (noch nicht implementiert).

        Args:
            item (str): Item ID
            target (str): Target Entity ID
        """
        pass


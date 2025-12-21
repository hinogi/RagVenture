import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


class GameModel:
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
        query = """
        MATCH (p:Player {id: 'player'})-[:IST_IN]->(location:Location)
        RETURN 
            location.id AS id, 
            location.name AS name, 
            location.description AS description,
            location.name_emb AS name_emb
        """
        return self._run_query(query)

    def location_content(self):
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
        query = """
        MATCH (p:Player {id: 'player'})-[:TRÄGT]->(inventory:Item)
        RETURN 
            inventory.id AS id,
            inventory.name AS name,
            inventory.name_emb AS name_emb
        """
        return self._run_query(query)

    def move_player(self, to_location):
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
        pass


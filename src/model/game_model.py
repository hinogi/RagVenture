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
            )
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

    def current_location():
        pass

    def current_inventory():
        pass

    def move_player():
        pass

    def take_item():
        pass
    
    def use_item():
        pass


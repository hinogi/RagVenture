import logging
from typing import List

from sentence_transformers import SentenceTransformer, util
from model.command_templates import COMMAND_TEMPLATES

# Singleton damit der speicher nicht so schnell ausgeht :)

class EmbeddingUtils:
    """
    Singleton für Embedding-basiertes Matching.
    
    Wird automatisch als Singleton behandelt - jeder Aufruf von 
    EmbeddingUtils() gibt die gleiche Instanz zurück.
    """

    _instance = None

    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            cls._instance.util = util
            
            cls._instance.command_emb = {}
            for templates in COMMAND_TEMPLATES:
                cls._instance.command_emb[templates.command] = cls._instance.model.encode(templates.verbs)
        
            logging.basicConfig(
                filename='parser_debug.log',
                level=logging.INFO,
                format='%(asctime)s - %(message)s'
            )

        return cls._instance

    def verb_to_command(self, verb):

        logging.info(f"=== Verb Input: '{verb}' ===")
        result =  []

        if verb is None:
            result.append({
                'command': None,
                'sim': 0.0
            })
            return result 

        verb_emb = self.model.encode(verb)

        for command, command_emb in self.command_emb.items():

            similarities = self.util.cos_sim(verb_emb, command_emb)
            max_sim = similarities.max().item()

            result.append({
                'command': command,
                'sim': max_sim
            })

        result.sort(key=lambda x: x['sim'], reverse=True)
        logging.info(f"=== Verb Output: {result} ===")
        return result
    
    def match_entities(self, query_text: str, states: dict):

        candidates = [x for x in states]

        logging.info(f"=== Noun Import: '{query_text}' | Candidates: {candidates} ===")
        result = []

        # Query embedden
        query_emb = self.model.encode(query_text)

        # Einzeln mit kandidaten vergleichen
        for candidate in candidates:

            score = self.util.cos_sim(query_emb, candidate['name_emb'])
            result.append({
                'id': candidate['id'],
                'name': candidate['name'],
                'score': score
            })

        # Nach similarity sortieren
        result.sort(key=lambda x: x['score'], reverse=True)
        logging.info(f"=== Noun Output: {result} ===")
        return result

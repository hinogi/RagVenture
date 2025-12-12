import spacy
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from utils.command_templates import COMMAND_TEMPLATES, CommandTemplate
from utils.embedding_utils import model, util

load_dotenv(dotenv_path='../.env')

class SmartParser:

    def __init__(self):

        # Models laden
        self.parsing_model = spacy.load("de_dep_news_trf")
        self.matching_model = model
        self.util = util

        # Commands embedden
        self.command_emb = {}

        for templates in COMMAND_TEMPLATES:
            self.command_emb[templates.command] = self.matching_model.encode(templates.verbs)

        logging.basicConfig(
            filename='parser_debug.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def _verb_to_command(self, verb):

        result =  {}

        if verb is None:
            result = {
                'best_command': None,
                'best_sim': 0.0
            }
            return result

        result = {
            'best_command': None,
            'best_sim': -1.0
        }

        verb_emb = self.matching_model.encode(verb)

        for command, command_emb in self.command_emb.items():

            similarities = self.util.cos_sim(verb_emb, command_emb)
            max_sim = similarities.max().item()

            logging.info(f"{max_sim}")

            if max_sim > result['best_sim']:
                result = {
                    'best_command': command,
                    'best_sim': max_sim
                }
        
        # Trashhold... 
        if result['best_sim'] < 0.90:
            result = {
                'best_command': None,
                'best_sim': 0.0
            }

        return result

    def parse(self, input_text):

        if not input_text or not input_text.strip():
            return [{'action': None, 'target': None, 'adjects': None, 'raw': input_text}]
    
        input_syntax = self.parsing_model(input_text)
        
        results = {
            'action': None,
            'target': None,
            'raw': input_text
        }

        # Detailliertes Logging des Spacy Doc
        logging.info(f"=== Parsing Input: '{input_text}' ===")
        for token in input_syntax:
            logging.info(f"  Token: '{token.text:15}' | POS: {token.pos_:8} | DEP: {token.dep_:10} | Lemma: {token.lemma_:15} | Head: {token.head.text}")

        # Command bauen
        for token in input_syntax:

            # Hauptverb finden
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                match = self._verb_to_command(token.lemma_)
                logging.info(f"  → VERB gefunden: '{token.lemma_}' → Command: {match['best_command']} (Sim: {match['best_sim']:.2f})")
                results['action'] = match['best_command'] if match else None

            # Nomen/Objekte finden
            if token.pos_ in ['NOUN']:
                object_text = token.text
                logging.info(f"  → OBJEKT gefunden: '{token.text}' (dep: {token.dep_})")

                # Adjektiv finden wenn vorhanden
                # for child in token.children:
                #     if child.pos_ == 'ADJ':
                #         object_text = f"{child.text} {object_text}"
                #         logging.info(f"     + Adjektiv: '{child.text}' → '{object_text}'")

                results['target'] = object_text

        logging.info(f"  → FINAL RESULT: action={results['action']}, target={results['target']}")
        logging.info("")

        return [results]

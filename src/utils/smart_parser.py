import os
import spacy 
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer, util
from utils.command_templates import COMMAND_TEMPLATES, CommandTemplate

load_dotenv(dotenv_path='../.env')


class SmartParser:

    def __init__(self):

        # Models laden
        self.parsing_model = spacy.load("de_dep_news_trf")
        self.matching_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Commands embedden
        self.command_emb = {}

        for templates in COMMAND_TEMPLATES:
            self.command_emb[templates.command] = self.matching_model.encode(templates.verbs)
    
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

            similarities = util.cos_sim(verb_emb, command_emb)
            max_sim = similarities.max().item()

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
            return [{'action': None, 'targets': [], 'adjects': [], 'raw': input_text}]
    
        doc = self.parsing_model(input_text)
        
        results = {
            'action': None,
            'targets': [],
            'raw': input_text
        }

        for token in doc:

            # Hauptverb finden
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                match = self._verb_to_command(token.lemma_)
                results['action'] = match['best_command'] if match else None

            # Nomen/Objekte finden
            if token.dep_ in ['obj', 'dobj', 'oa', 'pobj']:
                object_text = token.text

                # Adjektiv finden wenn vorhanden
                for child in token.children:
                    if child.pos_ == 'ADJ':
                        object_text = f"{child.text} {object_text}"
                
                results['targets'].append(object_text)
        
        return [results]

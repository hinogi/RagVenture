import spacy
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

class SmartParser:

    def __init__(self):

        self.parsing_model = spacy.load("de_dep_news_trf")

        logging.basicConfig(
            filename='parser_debug.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def parse(self, input_text):

        if not input_text or not input_text.strip():
            return [{'verb': None, 'noun': None, 'adjects': None, 'raw': input_text}]
    
        input_syntax = self.parsing_model(input_text)

        verb = []
        
        results = {
            'verb': None,
            'noun': None,
            'adjects': None,
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
                verb = [token.lemma_]
        
                for child in token.children:
                    if child.dep_ == 'oc':
                        verb.insert(0, child.lemma_)

            # Nomen/Objekte finden
            if token.pos_ in ['NOUN']:
                results['noun'] = token.text

        results['verb'] = ' '.join(verb)
        
        logging.info(f"=== Parsing Output: {results} ===")
        return [results]
 

import logging
from view.game_view import GameView
from model.game_model import GameModel
from utils.smart_parser import SmartParser
from utils.embedding_utils import EmbeddingUtils

class GameController:

    def __init__(self):
        
        self.view = GameView()
        self.model = GameModel()
        self.parser = SmartParser()
        
        self.embedding_utils = EmbeddingUtils()
        
        self.game_state = {}
        self.game_running = False

        logging.basicConfig(
            filename='parser_debug.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def _update_game_state(self):

        self.game_state = {
            'location': self.model.current_location(),
            'items': self.model.location_content(),
            'exits': self.model.location_exits(),
            'inventory': self.model.player_inventory()
        }
        
        logging.info(f"State: {self.game_state}")
        self.view.update_panels(**self.game_state)

    def run_game(self):
        self.game_running = True

        self.view.show_welcome()
        input()
        self._update_game_state()

        self.view.refresh()

        while self.game_running:
            user_input = self.view.get_input()
            status = self.process_input(user_input)
            self._update_game_state()
            self.view.refresh(status=status)
    
    def process_input(self, input):

        if input == 'quit':
            self.game_running = False
            return "Auf Wiedersehen!"

        parsed = self.parser.parse(input)

        verb = parsed[0]['verb']
        noun = parsed[0]['noun']

        command = self.embedding_utils.verb_to_command(verb)
        
        if command['best_command'] == 'go':

            if not noun:
                return f"Wohin genau?"
            else:
                # Ziel finden
                exit = self.embedding_utils.match_entities(
                    noun, 
                    [x for x in self.game_state['exits']]
                )
                result = self.model.move_player(exit[0]['id'])

                if result:
                    return f'Du bist jetzt in {result[0]['name']}'
                else:
                    return 'Ups, gestolpert?'

        elif command['best_command'] == 'take':
            if not noun:
                return"Was genau?"
            else:
                item = self.embedding_utils.match_entities(
                    noun, 
                    [x for x in self.game_state['items']]
                )
                result = self.model.take_item(item[0]['id'])

                
                if result:
                    return f'Du trägst jetzt {result[0]['name']}'
                else:
                    return 'Ups, fallengelassen?'

        elif command['best_command'] == 'drop':
            if not noun:
                return "Was denn?"
            else:
                item = self.embedding_utils.match_entities(
                    noun,
                    [x for x in self.game_state['inventory']]
                )
                result = self.model.drop_item(item[0]['id'])
                
                if result:
                    return f'Du hast {result[0]['name']} abgelegt.'
                else:
                    return 'Ups, nicht da?'

        else:
            return f"Das konnte nicht entschlüsselt werden."
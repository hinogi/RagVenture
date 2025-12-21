
import logging
from view.game_view import GameView
from model.world_model import GameModel
from model.game_state import GameState
from model.conversation_state import ConversationState
from utils.smart_parser import SmartParserUtils
from utils.embedding_utils import EmbeddingUtils
from utils.conversation_system import ConversationUtils

class GameController:

    def __init__(self):
        
        # init pattern
        self.view = GameView()
        self.model = GameModel()

        # load utils
        self.parser_utils = SmartParserUtils()        
        self.embedding_utils = EmbeddingUtils()
        self.conversation_utils = ConversationUtils()
        
        # init states
        self.game_state = GameState()
        self.converation_state = ConversationState()

    def _update_game_state(self):

        self.game_state = {
            'location': self.model.current_location(),
            'items': self.model.location_content(),
            'exits': self.model.location_exits(),
            'inventory': self.model.player_inventory()
        }
        
        logging.info(f"*** Game State: {self.game_state} ***")
        self.view.update_panels(**self.game_state)
    
    def _run_game(self, state: bool):
        self.game_state.running = state

    def run_game(self):
        self._run_game(True)

        # Intro :)
        self.view.show_welcome()
        input()

        while self.game_running:

            # Check conversation
            if self.conversation.has_pending_question():
                continue

            # Parsing
            parsed = self.parser.parse(input)
            verb = parsed[0]['verb']
            noun = parsed[0]['noun']

            # Commanding
            commands = self.embedding_utils.verb_to_command(verb)
            good_commands = [c for c in commands if c['sim'] >= .95]

            if len(good_commands) >= 2 or len(good_commands) == 0:
                logging.info(f"=== Validate Verb: {good_commands} ===")
                return f"Was möchtest du tun?"
            else:
                best_command = good_commands[0]['command']

            # run command
            status = self.process_input(user_input)
            self._update_game_state()
            self.view.refresh(status=status)

            # Prompt
            user_input = self.view.get_input()

            if input == 'quit':
                self.game_running = False
                return "Auf Wiedersehen!"

    
    def process_input(self, input):

        if best_command == 'go':

            if not noun:
                return f"Wohin genau?"
            else:
                # Ziel finden
                exit = self.embedding_utils.match_entities(
                    noun, 
                    self.game_state['exits']
                )

                result = self.model.move_player(exit[0]['id'])

                if result:
                    return f'Du bist jetzt in {result[0]['name']}'
                else:
                    return 'Ups, gestolpert?'

        elif best_command == 'take':
            if not noun:
                return"Was genau?"
            else:
                item = self.embedding_utils.match_entities(
                    noun, 
                    self.game_state['items']
                )
                result = self.model.take_item(item[0]['id'])

                
                if result:
                    return f'Du trägst jetzt {result[0]['name']}'
                else:
                    return 'Ups, fallengelassen?'

        elif best_command == 'drop':
            if not noun:
                return "Was denn?"
            else:
                item = self.embedding_utils.match_entities(
                    noun,
                    self.game_state['inventory']
                )
                result = self.model.drop_item(item[0]['id'])
                
                if result:
                    return f'Du hast {result[0]['name']} abgelegt.'
                else:
                    return 'Ups, nicht da?'

        else:
            return f"Das konnte nicht entschlüsselt werden."
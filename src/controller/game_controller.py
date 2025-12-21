import logging
from view.game_view import GameView
from model.world_model import GameModel
from model.game_state import GameState
from utils.smart_parser import SmartParserUtils
from utils.embedding_utils import EmbeddingUtils

class GameController:

    def __init__(self):
        
        # init pattern
        self.view = GameView()
        self.model = GameModel()

        # load utils
        self.parser_utils = SmartParserUtils()        
        self.embedding_utils = EmbeddingUtils()
        
        # init states
        self.state = GameState()

    def run_game(self):
        self.state.set_run_state(True)

        # Intro :)
        self.view.show_welcome()
        input()

        while self.state.running:

            # Check conversation
            if self.conversation.status == 'PROMPT':
                self.conversation.input = self.view.get_input()

            # Parsing
            parsed = self.parser_utils.parse(input)
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
            status = self.process_input(self.conversation.input)

            # update latest game_states
            self.world.update_world_state(
                location= self.model.current_location(),
                items= self.model.location_content(),
                exits= self.model.location_exits(),
                inventory= self.model.player_inventory()
            )

            self.view.update_panels(**self.state)
            self.view.refresh(status=status)

            # Prompt

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
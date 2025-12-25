import logging
from view.game_view import GameView
from model.world_model import GameModel
from model.game_state import GameState, Status
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
        self.state.running = True

        # Intro :)
        self.view.show_welcome()
        input()

        while self.state.running:

            location= self.model.current_location()
            items= self.model.location_content()
            exits= self.model.location_exits()
            inventory= self.model.player_inventory()

            # rendering
            self.view.update_panels(location, items, exits, inventory, self.state.message)
            self.view.refresh(status=self.state.message)

            # get input
            self.state.input = self.view.get_input()

            if self.state.input == 'quit':
                self.state.running = False
                break

            if self.state.loop_state == Status.PARSE:

                # Parsing
                parsed = self.parser_utils.parse(self.state.input)
                self.state.verb = parsed[0]['verb']
                self.state.noun = parsed[0]['noun']

                # State
                self.state.loop_state = Status.VERIFY

            if self.state.loop_state == Status.VERIFY:

                # Command matching
                commands = self.embedding_utils.verb_to_command(self.state.verb)
                good_commands = [c for c in commands if c['sim'] >= .95]

                if len(good_commands) > 1 or len(good_commands) == 0:
                    self.state.command_list = good_commands

                # Target matching
                all_targets = self._handle_target_candidates(exits, items, inventory)
                sim_targets = self.embedding_utils.match_entities(self.state.noun, all_targets)
                good_targets = [t for t in sim_targets if t['score'] >= .75]

                if len(good_targets) > 1 or len(good_targets) == 0:
                    self.state.target_list = good_targets
                
                self.state.loop_state = Status.REQUEST

            # run command
            status = self.process_input(self.conversation.input)

    def _handle_target_candidates(self, exits, items, inventory):

        candidates = []
        
        for e in exits:
            e['type'] = 'exit'
            candidates.append(e)
        for i in items:
            i['type'] = 'item'
            candidates.append(i)
        for i in inventory:
            i['type'] = 'inventory'
            candidates.append(i)
        
        return candidates

    def _handle_parse(self):
        pass

    def _handle_choise(self):
        pass



    ## TODO: refactoring ##########
    
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
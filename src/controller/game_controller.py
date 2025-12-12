
import logging
from view.game_view import GameView
from model.game_model import GameModel
from utils.smart_parser import SmartParser

class GameController:

    def __init__(self):
        self.view = GameView()
        self.model = GameModel()
        self.parser = SmartParser()
        self.running = False

        logging.basicConfig(
            filename='parser_debug.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def _update_game_state(self):

        self.view.update_panels(
            location = self.model.current_location(),
            items = self.model.location_content(),
            exits = self.model.location_connections(),
            inventory = self.model.player_inventory()
        )

    def run_game(self):
        self.running = True

        self.view.show_welcome()
        input()
        self._update_game_state()

        self.view.refresh()

        while self.running:
            command = self.view.get_command()
            status = self.process_command(command)
            self._update_game_state()
            self.view.refresh(status=status)
    
    def process_command(self, command):

        if command == 'quit':
            self.running = False
            return "Auf Wiedersehen!"

        parsed = self.parser.parse(command)

        action = parsed[0]['action']
        target = parsed[0]['target']

        # print(parsed)
        
        if action == 'go':
            if not target:
                return f"Wohin genau? {parsed}"
                

            else:

                # Ziel finden
                locations = self.model.match_locations(target)
                logging.info(f"LOCATION: {locations}")

                result = self.model.move_player(locations[0]['location_id'])

                if result:
                    return f'Du bist jetzt in {result[0]['target.name']}\n'
                else:
                    return 'Ups, gestolpert.'

        elif action == 'take':
            if not target:
                result = self.model.location_item()
                return"Was genau?"

            else:
                result = self.model.take_item(target[0])
                
                if result:
                    return f'Du trägst jetzt {result[0]['i.name']}'

        elif action == 'drop':
            if not target:
                result = self.model.player_inventory()
                return "Fallengelassen sag ich mal"

            else:
                result = self.model.drop_item(target[0])
                
                if result:
                    return f'Du hast {result[0]['i.name']} abgelegt.'

        else:
            return f"Das konnte nicht entschlüsselt werden."
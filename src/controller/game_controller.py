
from view.game_view import GameView
from model.game_model import GameModel
from utils.smart_parser import SmartParser

class GameController:

    def __init__(self):
        self.view = GameView()
        self.model = GameModel()
        self.parser = SmartParser()
        self.running = False

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
        targets = parsed[0]['targets']

        # print(parsed)
        
        if action == 'go':
            if not targets:
                return f"Wohin genau? {parsed}"
                

            else:
                result = self.model.move_player(targets[0])

                if result:
                    return f'Du bist jetzt in {result[0]['target.name']}\n'
                else:
                    return 'Ups, gestolpert.'

        elif action == 'take':
            if not targets:
                result = self.model.location_item()
                return"Was genau?"

            else:
                result = self.model.take_item(targets[0])
                
                if result:
                    return f'Du trägst jetzt {result[0]['i.name']}'

        elif action == 'drop':
            if not targets:
                result = self.model.player_inventory()
                return "Fallengelassen sag ich mal"

            else:
                result = self.model.drop_item(targets[0])
                
                if result:
                    return f'Du hast {result[0]['i.name']} abgelegt.'

        else:
            return f"Das konnte nicht entschlüsselt werden."
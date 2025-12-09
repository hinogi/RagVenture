
from view.game_view import GameView
from model.game_model import GameModel
from utils.smart_parser import SmartParser

class GameController:

    def __init__(self):
        self.view = GameView()
        self.model = GameModel()
        self.parser = SmartParser()
        self.running = False

    def run_game(self):
        self.running = True

        self.view.show_welcome()
        input()
        # Daten fetchen #
        self.view.start_game(
            location = 'Marktplatz',
            items = 'Items: Schlüssel, goldener Esel',
            exits = 'Exits: Taverne',
            inventory = 'A\nB\nC'
        )

        self.view.refresh()

        while self.running:
            command = self.view.get_command()
            self.process_command(command)
            self.view.refresh()
    
    def process_command(self, command):

        parsed = self.parser.parse(command)

        action = parsed[0]['action']
        targets = parsed[0]['targets']

        print(parsed)

        if action == 'quit':

            self.running = False
            self.view.show_message('Tschüss!')

        elif action == 'look':

            if not targets:
                self.view.show_message('Was möchtest Du sehen ("show ...)"?')
                return

            target = targets[0]

            if target == 'inventory':
                result = self.model.player_inventory()
            elif target == 'location':
                result = self.model.current_location()
            elif target == 'directions':
                result = self.model.location_connections()
            elif target == 'content':
                result = self.model.location_content()
            else:
                self.view.show_message(f"Was ist {target}?")
                return

            self.view.show_list('Hier gibts: ', result)
        
        elif action == 'go':
            if not targets:
                result = self.model.location_connections()

                self.view.show_list("Erreichbare Orte", result)
                return

            else:
                result = self.model.move_player(targets[0])
                location = self.model.location_content()

                if result:
                    self.view.show_message(f'Du bist jetzt in {result[0]['target.name']}\n')
                    self.view.show_message(location)
                else:
                    self.view.show_message('Ups, gestolpert.')

        elif action == 'take':
            if not targets:
                result = self.model.location_item()
                self.view.show_list("Objekte: ", result)
                return

            else:
                result = self.model.take_item(targets[0])
                
                if result:
                    self.view.show_message(f'Du trägst jetzt {result[0]['i.name']}')
                    return

        elif action == 'drop':
            if not targets:
                result = self.model.player_inventory()
                self.view.show_list("Inventory: ", result)
                return

            else:
                result = self.model.drop_item(targets[0])
                
                if result:
                    self.view.show_message(f'Du hast {result[0]['i.name']} abgelegt.')
                    return

        else:
            self.view.show_message(f"Befehlt {action} nicht erkannt. Verwende 'show ...', 'visit ...', 'quit'")
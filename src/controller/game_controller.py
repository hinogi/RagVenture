
from view.game_view import GameView
from model.game_model import GameModel
from utils.command_parser import CommandParser

class GameController:

    def __init__(self):
        self.view = GameView()
        self.model = GameModel()
        self.parser = CommandParser()
        self.running = False

    def run_game(self):
        self.running = True
        self.view.show_welcome()

        while self.running:
            command = self.view.get_command()
            self.process_command(command)
    
    def process_command(self, command):

        parsed = self.parser.parse(command)

        action = parsed['action']
        targets = parsed['targets']

        if action == 'quit':

            self.running = False
            self.view.show_message('Tschüss!')

        elif action == 'show':

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
            else:
                self.view.show_message(f"Was ist {target}?")
                return

            self.view.show_message(result)
        
        elif action == 'visit':
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
                result = self.model.take_item(targets)
                
                if result:
                    self.view.show_message(f'Du trägst jetzt {result[0]['i.name']}')
                    return

        else:
            self.view.show_message(f"Befehlt {action} nicht erkannt. Verwende 'show ...', 'visit ...', 'quit'")
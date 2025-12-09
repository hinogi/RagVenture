from rich.prompt import Prompt
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
import os
import platform


class GameView:
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self._create_layout()
    
    def _create_layout(self):

        # Horizontal aufteilen
        self.layout.split_row(
            Layout(name='main', ratio=3),
            Layout(name='inventory', ratio=1)
        )

        self.layout['main'].split_column(
            Layout(name='location', ratio=1),
            Layout(name='items', ratio=4),
            Layout(name='exits', ratio=2)
        )

    def show_welcome(self):
        self.console.clear()
        self.console.print(Panel(
            'Willkommen beim RagVenture',
            subtitle='NLP Lernsoftware ;-)',
            border_style='yellow',
            padding=(2, 2)
        ))

    def start_game(self, location, items, exits, inventory):
        self.layout['location'].update(Panel(location))
        self.layout['items'].update(Panel(items))
        self.layout['exits'].update(Panel(exits))
        self.layout['inventory'].update(Panel(inventory))

    def refresh(self):
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

        max_height = self.console.height - 4
        self.console.print(self.layout, crop=True, height=max_height)

    def get_command(self):
        return Prompt.ask('What? ')

    def show_message(self, prompt):
        self.console.print(f'Antwort: {prompt}')
    
    def show_list(self, title, data):
        if not data:
            self.console.print(f"[dim]Da ist nichts.[/dim]")
            return

        self.console.print(f'{title}')

        for item in data:
            self.console.print(item)

from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel


class GameView:
    
    def __init__(self):
        self.console = Console()

    def show_welcome(self):
        self.console.clear()
        self.console.print(Panel(
            'Willkommen beim RagVenture',
            subtitle='Weiter mit <G>',
            border_style='yellow',
            padding=(2, 2)
        ))

    def get_command(self):
        return Prompt.ask('What?')

    def show_message(self, prompt):
        self.console.print(f'Antwort: {prompt}')
    
    def show_list(self, title, data):
        if not data:
            self.console.print(f"[dim]Da ist nichts.[/dim]")
            return

        self.console.print(f'{title}')

        for item in data:
            self.console.print(item)

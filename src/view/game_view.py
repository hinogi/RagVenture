import os
import platform
from rich.panel import Panel
from rich.prompt import Prompt
from rich.layout import Layout
from rich.console import Console


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
            Layout(name='location_relateds'),
            Layout(name='conversation'),
        )

        self.layout['location_relateds'].split_row(
            Layout(name='items'),
            Layout(name='exits')
        )

    def show_welcome(self):
        self.console.clear()
        self.console.print(Panel(
            'Willkommen beim RagVenture',
            subtitle='NLP Lernsoftware ;-)',
            border_style='yellow',
            padding=(2, 2)
        ))

    def update_panels(self, location, items, exits, inventory):

        location_formated = f"[bold yellow]{location[0]['name']}[/bold yellow]\n{location[0]['description']}"

        if items:
            items_formated = '[bold yellow]Items[/bold yellow]'    
            for item in items:
                items_formated += f'\n{item['name']}. {item['description']}'
        else:
            items_formated = "Keine Gegenstände zu sehen"

        if exits:
            exits_formated = '[bold yellow]Exits[/bold yellow]'    
            for exit in exits:
                exits_formated += f'\n{exit['name']}'
        else:
            exits_formated = "Keine Ausgänge zu sehen"

        if inventory:
            inventory_formated = '[bold yellow]Inventar[/bold yellow]'    
            for item in inventory:
                inventory_formated += f'\n{item['name']}'
        else:
            inventory_formated = "Nichts dabei"

        self.layout['location'].update(Panel(location_formated))
        self.layout['items'].update(Panel(items_formated))
        self.layout['exits'].update(Panel(exits_formated))
        self.layout['inventory'].update(Panel(inventory_formated))

    def refresh(self, status=''):
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

        max_height = self.console.height - 4
        self.console.print(self.layout, crop=True, height=max_height)
        if status:
            self.console.print(f"\n{status}\n")

    def get_input(self):
        return Prompt.ask('>>> ')

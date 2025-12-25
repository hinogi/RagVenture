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
            Layout(name='dialog'),
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

    def update_location(self, location):
        location_formated = f"[bold yellow]{location[0]['name']}[/bold yellow]\n{location[0]['description']}"
        self.layout['location'].update(Panel(location_formated))

    def update_items(self, items):
        if items:
            items_formated = '[bold yellow]Items[/bold yellow]'    
            for item in items:
                items_formated += f'\n{item['name']}. {item['description']}'
        else:
            items_formated = "Keine Gegenstände zu sehen"
        self.layout['items'].update(Panel(items_formated))


    def update_exits(self, exits):
        if exits:
            exits_formated = '[bold yellow]Exits[/bold yellow]'    
            for exit in exits:
                exits_formated += f'\n{exit['name']}'
        else:
            exits_formated = "Keine Ausgänge zu sehen"
        self.layout['exits'].update(Panel(exits_formated))

    def update_inventory(self, inventory):
        if inventory:
            inventory_formated = '[bold yellow]Inventar[/bold yellow]'    
            for item in inventory:
                inventory_formated += f'\n{item['name']}'
        else:
            inventory_formated = "Nichts dabei"
        self.layout['inventory'].update(Panel(inventory_formated))


    def update_dialog(self, dialog):
        content = ''

        if dialog.type == 'message':
            content = dialog.text
        elif dialog.type == 'request_verb':
            for i, choice in enumerate(dialog.choices, 1):
                content += f"({i}) {choice} | "

        content = "(0) abbrechen "
        self.layout['dialog'].update(Panel(content or "..."))


    def refresh(self):
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

        max_height = self.console.height - 4
        self.console.print(self.layout, crop=True, height=max_height)

    def get_input(self):
        return Prompt.ask('>>> ')

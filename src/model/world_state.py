from enum import Enum
from dataclasses import dataclass, field


@dataclass
class WorldState:
    location: str | None = None
    items: list | None
    exits: list | None
    inventory: list | None

    def update_world_state(self, location, items, exits, inventory):
        self.state = {
            self.location: location,
            self.items: items,
            self.exits: exits,
            self.inventory: inventory
        }

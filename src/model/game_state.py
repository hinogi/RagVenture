from dataclasses import dataclass

@dataclass
class GameState():
    running: bool = False
    location: str | None = None
    items: list | None
    exits: list | None
    inventory: list | None

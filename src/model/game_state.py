from dataclasses import dataclass, field
from model.world_state import WorldState
from model.conversation_state import ConversationState


@dataclass
class GameState:
    running: bool = False
    game: WorldState = field(default_factory=WorldState)
    conversation: ConversationState = field(default_factory=ConversationState)

    def set_run_state(self, state):
        self.running = state
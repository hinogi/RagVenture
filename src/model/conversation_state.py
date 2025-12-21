from enum import Enum
from dataclasses import dataclass

class Status(Enum):
    PROMPT = 'wait_for_promt'
    REQUEST = 'wait_for_choice'

@dataclass
class ActionSteps:
    verb: str
    noun: str | None

@dataclass
class ConversationState:
    status: Status = Status.PROMPT
    question: str | None = None
    actions: list[ActionSteps]
    options: list[dict]
    message: str | None = None
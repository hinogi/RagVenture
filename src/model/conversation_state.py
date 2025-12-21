from enum import Enum
from dataclasses import dataclass


class Status(Enum):
    PROMPT = 'wait_for_prompt'
    PARSE = 'wait_for_parsing'
    REQUEST = 'wait_for_choice'

@dataclass
class ActionSteps:
    verb: str
    noun: str | None

@dataclass
class ConversationState:
    status: Status = Status.PROMPT
    input: str | None = None
    actions: list[ActionSteps]
    options: list[dict]
    message: str | None = None

    # insert input inklsive satae wechseln zu parse

    # statewechsel zu request

    # statewechsel zu prompt
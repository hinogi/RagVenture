from enum import Enum
from dataclasses import dataclass, field


class Status(Enum):
    PARSE = 'wait_for_parsing'   # Wenn Eingaben durch den Parser müssen (Input zu Vern/Noun)
    VERIFY = 'wait_for_verify'   # Wenn command und target verifiziert werden müssen (Verb/Noun zu Command/Target)
    REQUEST = 'wait_for_answers' # Wenn eine Auswahl getroffen werden muss
    ACTION = 'wait_for_action'   # Wenn eine Action ausgeführt werden kann

@dataclass
class GameState:
    running: bool = False
    loop_state: Status = Status.PARSE

    input: str | None = None

    verb: list | None = None
    noun: list | None = None

    command_list: list | None = None
    target_list: list | None = None

    message: str | None = None
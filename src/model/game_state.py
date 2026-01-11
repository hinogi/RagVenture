from enum import Enum
from dataclasses import dataclass, field

class LoopState(Enum):
    PARSE = 'wait_for_parsing'   # Wenn Eingaben durch den Parser müssen (Input zu Vern/Noun)
    VERIFY = 'wait_for_verify'   # Wenn command und target verifiziert werden müssen (Verb/Noun zu Command/Target)
    REQUEST = 'wait_for_answers' # Wenn eine Auswahl getroffen werden muss
    ACTION = 'wait_for_action'   # Wenn eine Action ausgeführt werden kann

@dataclass
class Parse:
    input: str | None = None
    verb: list | None = None
    noun: list | None = None
    good_commands: list = field(default_factory=list)
    good_targets: list = field(default_factory=list)

class DialogState(Enum):
    NONE = 'none'
    MESSAGE = 'message'
    REQUEST_VERB = 'request_verb'
    REQUEST_NOUN = 'request_noun'

@dataclass
class Dialog:
    type: DialogState = DialogState.MESSAGE
    message: str | None = None
    choices: list = field(default_factory=list)

class ActionCommands(Enum):
    GO = 'go'
    TAKE = 'take'
    DROP = 'drop'

@dataclass
class Action:
    command: ActionCommands | None = None
    target: str | None = None


@dataclass
class GameState:
    running: bool = False
    loop_state: LoopState = LoopState.PARSE

    parse: Parse = field(default_factory=Parse)
    dialog: Dialog = field(default_factory=Dialog)
    action: Action = field(default_factory=Action)


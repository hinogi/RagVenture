"""
Game State Dataclasses und Enums für State-Machine.

Definiert die komplette State-Struktur des Spiels: LoopState, Parse,
Dialog, Action und GameState für den Controller.
"""

from enum import Enum
from dataclasses import dataclass, field

class LoopState(Enum):
    """State-Machine States für den Game Loop."""
    PARSE = 'wait_for_parsing'   # Wenn Eingaben durch den Parser müssen (Input zu Vern/Noun)
    VERIFY = 'wait_for_verify'   # Wenn command und target verifiziert werden müssen (Verb/Noun zu Command/Target)
    REQUEST = 'wait_for_answers' # Wenn eine Auswahl getroffen werden muss
    ACTION = 'wait_for_action'   # Wenn eine Action ausgeführt werden kann

@dataclass
class Parse:
    """
    Parser-State mit Input und extrahierten Werten.

    Speichert User-Input, geparste Verb/Noun und gefundene Matches
    aus dem Embedding-Matching (good_commands, good_targets).
    """
    input: str | None = None
    verb: list | None = None
    noun: list | None = None
    good_commands: list = field(default_factory=list)
    good_targets: list = field(default_factory=list)

class DialogState(Enum):
    """Dialog-Typen für User-Interaktion."""
    NONE = 'none'
    MESSAGE = 'message'
    REQUEST = 'request'

@dataclass
class Dialog:
    """
    Dialog-State für User-Feedback und Requests.

    Speichert Typ (MESSAGE/REQUEST_VERB/REQUEST_NOUN), Nachricht
    und Auswahlmöglichkeiten für mehrdeutige Matches.
    """
    type: DialogState = DialogState.MESSAGE
    message: str | None = None
    choices: list = field(default_factory=list)

class ActionCommands(Enum):
    """Verfügbare Spiel-Commands."""
    GO = 'go'
    TAKE = 'take'
    DROP = 'drop'

@dataclass
class Action:
    """
    Validierte Action die ausgeführt werden soll.

    Enthält Command (GO/TAKE/DROP) und Target (Entity-ID) nach
    erfolgreichem Matching in VERIFY oder REQUEST.
    """
    command: ActionCommands | None = None
    target: str | None = None


@dataclass
class GameState:
    """
    Haupt-State des Spiels.

    Kombiniert alle Sub-States (Parse, Dialog, Action) und steuert
    den State-Machine Flow via loop_state.
    """
    running: bool = False
    loop_state: LoopState = LoopState.PARSE

    parse: Parse = field(default_factory=Parse)
    dialog: Dialog = field(default_factory=Dialog)
    action: Action = field(default_factory=Action)


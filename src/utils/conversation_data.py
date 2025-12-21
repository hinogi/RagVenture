from dataclasses import dataclass
from typing import List

@dataclass
class Action:
    command: str
    targets: List[dict]
    verb: str
    noun: str | None

@dataclass
class Command:
    status: str
    question: str
    action: Action
    options: List[dict]
    message: str
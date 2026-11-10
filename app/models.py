from enum import Enum
from dataclasses import dataclass
from typing import Any

class StateFlag(str, Enum):
    WAIT_RATE = "WAIT_RATE"
    CALLING = 'CALLING'
    DONE = 'DONE'
    FAILED = 'FAILED'

@dataclass
class Job:
    req_no: str
    document_path: str
    state: StateFlag
    result: Any = None
    error: str | None = None

from enum import Enum


class SessionState(str, Enum):
    IDLE = "idle"
    COMPILING = "compiling"
    EXECUTING = "executing"


class SessionStateMachine:
    def __init__(self) -> None:
        self.state = SessionState.IDLE

    def start_compile(self) -> bool:
        if self.state != SessionState.IDLE:
            return False
        self.state = SessionState.COMPILING
        return True

    def start_exec(self) -> bool:
        if self.state != SessionState.COMPILING:
            return False
        self.state = SessionState.EXECUTING
        return True

    def reset_idle(self) -> None:
        self.state = SessionState.IDLE

    def accepts_stdin(self) -> bool:
        return self.state == SessionState.EXECUTING

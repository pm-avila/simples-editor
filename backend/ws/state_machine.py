from enum import Enum


class SessionState(Enum):
    IDLE = "idle"
    COMPILING = "compiling"
    EXECUTING = "executing"


class SessionStateMachine:
    def __init__(self) -> None:
        self.state = SessionState.IDLE

    def start_compile(self) -> None:
        self.state = SessionState.COMPILING

    def start_exec(self) -> None:
        self.state = SessionState.EXECUTING

    def reset_idle(self) -> None:
        self.state = SessionState.IDLE

    def accepts_stdin(self) -> bool:
        return self.state == SessionState.EXECUTING

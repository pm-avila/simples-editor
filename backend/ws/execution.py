from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ExecutionStrategyError(Exception):
    """Raised when execution lifecycle operations are invalid or fail."""


class ExecutionLifecycleState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass
class ExecutionHandle:
    container: object
    stdin_socket: object


class ExecutionStrategy(Protocol):
    state: ExecutionLifecycleState

    def start(self, image: str, command: list[str]) -> ExecutionHandle: ...

    def send_stdin(self, data: str) -> None: ...

    def poll_stdout(self) -> str: ...

    def stop(self) -> None: ...

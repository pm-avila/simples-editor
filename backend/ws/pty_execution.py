from backend.ws.execution import ExecutionHandle
from backend.ws.execution import ExecutionLifecycleState
from backend.ws.execution import ExecutionStrategyError


class PtyExecutionStrategy:
    def __init__(self, client_factory=None):
        self._client_factory = client_factory or self._build_default_client
        self._client = None
        self._container = None
        self._stdin_socket = None
        self.state = ExecutionLifecycleState.IDLE

    def _build_default_client(self):
        try:
            import docker
        except ModuleNotFoundError as exc:
            raise ExecutionStrategyError("docker sdk unavailable") from exc
        return docker.from_env()

    def start(self, image: str, command: list[str]) -> ExecutionHandle:
        if self.state != ExecutionLifecycleState.IDLE:
            raise ExecutionStrategyError("execution already started")

        self._client = self._client_factory()
        try:
            container = self._client.containers.create(
                image=image,
                command=command,
                stdin_open=True,
                tty=True,
                working_dir="/sandbox",
                user="sandbox",
                detach=True,
            )
            container.start()
            stdin_socket = container.attach_socket(params={"stdin": 1, "stream": 1})
        except Exception as exc:
            raise ExecutionStrategyError("failed to initialize pty execution") from exc

        self._container = container
        self._stdin_socket = stdin_socket
        self.state = ExecutionLifecycleState.RUNNING
        return ExecutionHandle(container=container, stdin_socket=stdin_socket)

    def send_stdin(self, data: str) -> None:
        if self.state != ExecutionLifecycleState.RUNNING or self._stdin_socket is None:
            raise ExecutionStrategyError("execution is not running")
        payload = data.encode("utf-8") if isinstance(data, str) else data
        self._stdin_socket.send(payload)

    def poll_stdout(self) -> str:
        if self.state != ExecutionLifecycleState.RUNNING or self._container is None:
            raise ExecutionStrategyError("execution is not running")
        raw = self._container.logs(stdout=True, stderr=False) or b""
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)

    def stop(self) -> None:
        if self.state == ExecutionLifecycleState.STOPPED:
            return
        if self.state != ExecutionLifecycleState.RUNNING or self._container is None:
            raise ExecutionStrategyError("execution is not running")
        try:
            self._container.stop(timeout=1)
        except Exception as exc:
            raise ExecutionStrategyError("failed to stop execution") from exc
        self.state = ExecutionLifecycleState.STOPPED

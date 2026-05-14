import unittest

from backend.ws.execution import ExecutionLifecycleState
from backend.ws.execution import ExecutionStrategyError
from backend.ws.pty_execution import PtyExecutionStrategy


class _FakeSocket:
    def __init__(self):
        self.sent = []

    def send(self, data):
        self.sent.append(data)


class _FakeContainer:
    def __init__(self):
        self.started = False
        self.stopped = False
        self.stop_timeout = None
        self.socket = _FakeSocket()
        self.logs_output = b"stdout-line"

    def start(self):
        self.started = True

    def stop(self, timeout=1):
        self.stopped = True
        self.stop_timeout = timeout

    def attach_socket(self, params=None):
        return self.socket

    def logs(self, stdout=True, stderr=False):
        return self.logs_output


class _FakeDockerClient:
    def __init__(self):
        self.created = []
        self.container = _FakeContainer()
        self.containers = self

    def create(self, **kwargs):
        self.created.append(kwargs)
        return self.container


class PtyExecutionStrategyTest(unittest.TestCase):
    def test_starts_with_idle_state(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        self.assertEqual(strategy.state, ExecutionLifecycleState.IDLE)

    def test_send_stdin_requires_started_session(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        with self.assertRaises(ExecutionStrategyError):
            strategy.send_stdin("hello")

    def test_start_moves_state_to_running_and_second_start_is_rejected(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        strategy.start(image="simples-runner:dev", command=["/bin/sh"])
        self.assertEqual(strategy.state, ExecutionLifecycleState.RUNNING)
        with self.assertRaises(ExecutionStrategyError):
            strategy.start(image="simples-runner:dev", command=["/bin/sh"])

    def test_start_uses_prd_sandbox_isolation_defaults(self):
        client = _FakeDockerClient()
        strategy = PtyExecutionStrategy(client_factory=lambda: client)

        strategy.start(image="simples-runner:dev", command=["/bin/sh"])

        created = client.created[0]
        self.assertEqual(created["stdin_open"], True)
        self.assertEqual(created["tty"], True)
        self.assertEqual(created["working_dir"], "/sandbox")
        self.assertEqual(created["user"], "65534:65534")
        self.assertEqual(created["detach"], True)
        self.assertEqual(created["network_mode"], "none")
        self.assertEqual(created["read_only"], True)
        self.assertEqual(created["cap_drop"], ["ALL"])
        self.assertEqual(created["mem_limit"], "128m")
        self.assertEqual(created["memswap_limit"], "128m")
        self.assertEqual(created["cpu_quota"], 50000)
        self.assertEqual(created["pids_limit"], 64)
        self.assertEqual(created["tmpfs"], {"/tmp": "size=8m"})

    def test_stop_before_start_is_rejected(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        with self.assertRaises(ExecutionStrategyError):
            strategy.stop()

    def test_stop_after_start_transitions_to_stopped_and_is_idempotent(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        strategy.start(image="simples-runner:dev", command=["/bin/sh"])
        strategy.stop()
        self.assertEqual(strategy.state, ExecutionLifecycleState.STOPPED)
        strategy.stop()
        self.assertEqual(strategy.state, ExecutionLifecycleState.STOPPED)

    def test_stop_uses_hard_timeout_of_12_seconds(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        strategy.start(image="simples-runner:dev", command=["/bin/sh"])
        strategy.stop()
        self.assertEqual(strategy._container.stop_timeout, 12)

    def test_stdin_and_stdout_bridge_use_underlying_container_handles(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        strategy.start(image="simples-runner:dev", command=["/bin/sh"])
        strategy.send_stdin("input-1")
        self.assertIn(b"input-1", strategy._stdin_socket.sent)
        self.assertEqual(strategy.poll_stdout(), "stdout-line")


if __name__ == "__main__":
    unittest.main()

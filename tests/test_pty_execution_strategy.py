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
        self.socket = _FakeSocket()
        self.logs_output = b"stdout-line"

    def start(self):
        self.started = True

    def stop(self, timeout=1):
        self.stopped = True

    def attach_socket(self, params=None):
        return self.socket

    def logs(self, stdout=True, stderr=False):
        return self.logs_output


class _FakeDockerClient:
    def __init__(self):
        self.created = []
        self.container = _FakeContainer()
        self.containers = self

    def create(self, image, command, stdin_open, tty, working_dir, user, detach):
        self.created.append(
            {
                "image": image,
                "command": command,
                "stdin_open": stdin_open,
                "tty": tty,
                "working_dir": working_dir,
                "user": user,
                "detach": detach,
            }
        )
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

    def test_stdin_and_stdout_bridge_use_underlying_container_handles(self):
        strategy = PtyExecutionStrategy(client_factory=_FakeDockerClient)
        strategy.start(image="simples-runner:dev", command=["/bin/sh"])
        strategy.send_stdin("input-1")
        self.assertIn(b"input-1", strategy._stdin_socket.sent)
        self.assertEqual(strategy.poll_stdout(), "stdout-line")


if __name__ == "__main__":
    unittest.main()

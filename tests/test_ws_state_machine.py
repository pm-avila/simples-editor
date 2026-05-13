import backend.ws as backend_ws
from backend.ws.state_machine import SessionState
from backend.ws.state_machine import SessionStateMachine
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WebSocketScaffoldTest(unittest.TestCase):
    def test_backend_requirements_include_flask_sock(self):
        content = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("flask-sock==", content)

    def test_backend_ws_module_can_be_imported(self):
        self.assertIsNotNone(backend_ws)


class SessionStateMachineTest(unittest.TestCase):
    def test_new_machine_starts_idle(self):
        machine = SessionStateMachine()

        self.assertEqual(machine.state, SessionState.IDLE)

    def test_start_compile_transitions_to_compiling(self):
        machine = SessionStateMachine()

        machine.start_compile()

        self.assertEqual(machine.state, SessionState.COMPILING)

    def test_invalid_stdin_in_idle_rejected(self):
        machine = SessionStateMachine()

        self.assertFalse(machine.accepts_stdin())


if __name__ == "__main__":
    unittest.main()

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PTY_EXECUTION = ROOT / "backend" / "ws" / "pty_execution.py"


class SandboxEscapeAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PTY_EXECUTION.read_text(encoding="utf-8")

    def test_root_writes_are_blocked_by_read_only_filesystem(self):
        self.assertIn('read_only=True', self.source)
        self.assertIn('tmpfs={"/tmp": "size=8m"}', self.source)

    def test_fork_bombs_are_blocked_by_pid_limit(self):
        self.assertIn("pids_limit=64", self.source)

    def test_network_access_is_blocked_by_no_network_mode(self):
        self.assertIn('network_mode="none"', self.source)


if __name__ == "__main__":
    unittest.main()

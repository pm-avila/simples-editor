import io
import json
import unittest
from contextlib import redirect_stdout

from backend.observability import log_event


class StructuredLogTest(unittest.TestCase):
    def test_log_event_emits_json_line_with_required_fields(self):
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            log_event(
                "simples.executor",
                "execution_finished",
                user_id="user-123",
                request_id="req-123",
                duration_ms=234,
                exit_code=0,
            )

        payload = json.loads(buffer.getvalue().strip())
        self.assertEqual(payload["level"], "INFO")
        self.assertEqual(payload["logger"], "simples.executor")
        self.assertEqual(payload["event"], "execution_finished")
        self.assertEqual(payload["user_id"], "user-123")
        self.assertEqual(payload["request_id"], "req-123")
        self.assertEqual(payload["duration_ms"], 234)
        self.assertEqual(payload["exit_code"], 0)
        self.assertIn("timestamp", payload)


if __name__ == "__main__":
    unittest.main()

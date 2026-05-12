"""
Tests for compile timeout safeguards (issue #23).

Verifies that:
1. COMPILE_TIMEOUT env var is respected (configurable)
2. Invalid COMPILE_TIMEOUT values fall back to 15s safely
3. Timeout response is structured and client-friendly
4. subprocess.run receives the correct timeout parameter

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compile_timeout.py -v
"""
import subprocess
import unittest
from unittest.mock import MagicMock, call, patch

from backend.compiler import _parse_timeout


class TestParseTimeout(unittest.TestCase):
    """Unit tests for the timeout parsing helper."""

    def test_valid_integer_string_is_accepted(self):
        self.assertEqual(_parse_timeout("15"), 15)

    def test_custom_positive_value(self):
        self.assertEqual(_parse_timeout("30"), 30)

    def test_non_numeric_falls_back_to_default(self):
        self.assertEqual(_parse_timeout("abc"), 15)

    def test_empty_string_falls_back_to_default(self):
        self.assertEqual(_parse_timeout(""), 15)

    def test_none_falls_back_to_default(self):
        self.assertEqual(_parse_timeout(None), 15)  # type: ignore[arg-type]

    def test_zero_falls_back_to_default(self):
        self.assertEqual(_parse_timeout("0"), 15)

    def test_negative_falls_back_to_default(self):
        self.assertEqual(_parse_timeout("-5"), 15)

    def test_custom_default_is_used(self):
        self.assertEqual(_parse_timeout("bad", default=20), 20)

    def test_float_string_falls_back_to_default(self):
        """Float strings are not valid — int() would raise ValueError."""
        self.assertEqual(_parse_timeout("15.5"), 15)


class TestTimeoutPassedToSubprocess(unittest.TestCase):
    """Verify that compile_simples passes the configured timeout to subprocess.run."""

    def _make_success_run(self):
        def fake_run(cmd, capture_output, text, timeout):
            output_path = cmd[cmd.index("-o") + 1]
            with open(output_path, "w") as f:
                f.write("; nasm stub\n")
            proc = MagicMock()
            proc.returncode = 0
            proc.stderr = ""
            return proc
        return fake_run

    def test_subprocess_receives_compile_timeout(self):
        """The timeout kwarg passed to subprocess.run must equal COMPILE_TIMEOUT."""
        import backend.compiler as compiler_mod

        original = compiler_mod.COMPILE_TIMEOUT
        try:
            compiler_mod.COMPILE_TIMEOUT = 42
            with patch("backend.compiler.subprocess.run", side_effect=self._make_success_run()) as mock_run:
                from backend.compiler import compile_simples
                compile_simples("programa teste\ninicio\nfim\n")
            _, kwargs = mock_run.call_args
            self.assertEqual(kwargs.get("timeout", mock_run.call_args[0]), 42)
        finally:
            compiler_mod.COMPILE_TIMEOUT = original

    def test_timeout_expired_returns_structured_error(self):
        """TimeoutExpired must produce a JSON-serialisable error dict."""
        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            from backend.compiler import compile_simples
            result = compile_simples("programa teste\ninicio\nfim\n")

        self.assertFalse(result["ok"])
        error = result["error"]
        self.assertIn("phase", error)
        self.assertIn("line", error)
        self.assertIn("column", error)
        self.assertIn("message", error)

    def test_timeout_error_message_is_human_readable(self):
        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            from backend.compiler import compile_simples
            result = compile_simples("programa teste\ninicio\nfim\n")

        message = result["error"]["message"]
        self.assertIn("timeout", message.lower())

    def test_timeout_error_phase_is_compile(self):
        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            from backend.compiler import compile_simples
            result = compile_simples("programa teste\ninicio\nfim\n")

        self.assertEqual(result["error"]["phase"], "compile")


class TestTimeoutEndpointResponse(unittest.TestCase):
    """Verify the HTTP layer returns 422 with proper body on timeout."""

    def setUp(self):
        from backend.app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_endpoint_returns_422_on_timeout(self):
        import json

        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )

        self.assertEqual(resp.status_code, 422)
        body = resp.get_json()
        self.assertIn("error", body)
        self.assertIn("message", body["error"])
        self.assertIn("timeout", body["error"]["message"].lower())


if __name__ == "__main__":
    unittest.main()

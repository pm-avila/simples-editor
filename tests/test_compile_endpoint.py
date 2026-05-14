"""
Tests for POST /api/compile endpoint.

Run with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests/test_compile_endpoint.py -v
"""
import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch


SAMPLE_NASM = "section .text\n    global _start\n_start:\n    int 0x80\n"


def _mock_failure(stderr, returncode=1):
    """Return a side_effect that makes simplesc fail with stderr."""
    def fake_run(cmd, capture_output, text, timeout):
        proc = MagicMock()
        proc.returncode = returncode
        proc.stderr = stderr
        return proc
    return fake_run


class TestCompileEndpointSuccess(unittest.TestCase):

    def setUp(self):
        from backend.app import app  # lazy import to avoid polluting sys.modules early
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_returns_nasm_on_success(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("nasm", body)
        self.assertGreater(len(body["nasm"]), 0)
        self.assertRegex(body["nasm"], r"(section|global|mov|int 0x80)", "NASM contains expected directives")

    def test_post_compile_success_has_no_error_key(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
            content_type="application/json",
        )
        self.assertNotIn("error", resp.get_json())


class TestCompileEndpointFailure(unittest.TestCase):

    def setUp(self):
        from backend.app import app  # lazy import
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_returns_422_on_compiler_error(self):
        stderr = "4:7: erro: variavel 'y' nao declarada"
        with patch("backend.compiler.subprocess.run", side_effect=_mock_failure(stderr)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 422)

    def test_post_compile_error_has_structured_fields(self):
        stderr = "4:7: erro: variavel 'y' nao declarada"
        with patch("backend.compiler.subprocess.run", side_effect=_mock_failure(stderr)):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        error = resp.get_json()["error"]
        self.assertEqual(error["line"], 4)
        self.assertEqual(error["column"], 7)
        self.assertIn("variavel", error["message"])
        self.assertEqual(error["phase"], "compile")

    def test_post_compile_timeout_returns_422(self):
        def fake_timeout(cmd, capture_output, text, timeout):
            raise subprocess.TimeoutExpired(cmd, timeout)

        with patch("backend.compiler.subprocess.run", side_effect=fake_timeout):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 422)
        self.assertIn("timeout", resp.get_json()["error"]["message"])

    def test_post_compile_no_output_file_returns_422(self):
        """simplesc exits 0 but doesn't create the .asm file — should not 500."""
        def fake_no_output(cmd, capture_output, text, timeout):
            proc = MagicMock()
            proc.returncode = 0
            proc.stderr = ""
            return proc  # does NOT write asm_path

        with patch("backend.compiler.subprocess.run", side_effect=fake_no_output):
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )
        self.assertEqual(resp.status_code, 422)
        self.assertIn("output file", resp.get_json()["error"]["message"])

    def test_post_compile_returns_429_when_rate_limited(self):
        with patch("backend.app.allow_compile_request", return_value=(False, 17)), patch(
            "backend.app.compile_simples"
        ) as compile_mock:
            resp = self.client.post(
                "/api/compile",
                data=json.dumps({"code": "programa teste\ninicio\nfim\n"}),
                content_type="application/json",
            )

        compile_mock.assert_not_called()
        self.assertEqual(resp.status_code, 429)
        body = resp.get_json()
        self.assertEqual(body["error"]["phase"], "compile")
        self.assertEqual(body["error"]["retry_after"], 17)


class TestCompileEndpointValidation(unittest.TestCase):

    def setUp(self):
        from backend.app import app  # lazy import
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_post_compile_empty_code_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": ""}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_compile_missing_code_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_compile_whitespace_only_returns_400(self):
        resp = self.client.post(
            "/api/compile",
            data=json.dumps({"code": "   \n  "}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()

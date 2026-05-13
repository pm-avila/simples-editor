import importlib.util
import io
import json
import pathlib
import sys
import threading
import unittest
from contextlib import redirect_stdout
from types import ModuleType
from types import SimpleNamespace
from unittest.mock import patch

import jwt


ROOT = pathlib.Path(__file__).resolve().parents[1]


class WsHandshakeTokenExtractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "ws" / "handshake.py"
        spec = importlib.util.spec_from_file_location("backend.ws.handshake", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_extracts_subprotocol_bearer_dot_token(self):
        headers = {"Sec-WebSocket-Protocol": "simples.v1,bearer.token-abc"}

        token = self.module.extract_token_from_handshake(headers, {})

        self.assertEqual(token, "token-abc")

    def test_rejects_subprotocol_bearer_comma_token_format(self):
        headers = {"Sec-WebSocket-Protocol": "simples.v1,bearer,token-123"}

        with self.assertRaisesRegex(self.module.HandshakeAuthError, "missing bearer token"):
            self.module.extract_token_from_handshake(headers, {})

    def test_rejects_subprotocol_bearer_space_token_format(self):
        headers = {"Sec-WebSocket-Protocol": "simples.v1,bearer token-123"}

        with self.assertRaisesRegex(self.module.HandshakeAuthError, "missing bearer token"):
            self.module.extract_token_from_handshake(headers, {})

    def test_uses_query_token_as_fallback(self):
        headers = {}
        query_args = {"token": "query-token-456"}

        token = self.module.extract_token_from_handshake(headers, query_args)

        self.assertEqual(token, "query-token-456")

    def test_missing_token_raises_handshake_auth_error(self):
        with self.assertRaisesRegex(self.module.HandshakeAuthError, "missing bearer token"):
            self.module.extract_token_from_handshake({}, {})


class WsHandshakeAuthenticationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = ROOT / "backend" / "ws" / "handshake.py"
        spec = importlib.util.spec_from_file_location("backend.ws.handshake", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.module = module

    def test_authenticate_ws_handshake_returns_user_id(self):
        token = jwt.encode({"sub": "user-123"}, "secret", algorithm="HS256")

        user_id = self.module.authenticate_ws_handshake(
            {"Sec-WebSocket-Protocol": f"simples.v1,bearer.{token}"},
            {},
            "secret",
        )

        self.assertEqual(user_id, "user-123")

    def test_authenticate_ws_handshake_wraps_auth_error(self):
        with self.assertRaisesRegex(self.module.HandshakeAuthError, "invalid token"):
            self.module.authenticate_ws_handshake(
                {"Sec-WebSocket-Protocol": "simples.v1,bearer.not-a-jwt"},
                {},
                "secret",
            )

    def test_authenticate_ws_handshake_normalizes_auth_error_message(self):
        token = jwt.encode({}, "secret", algorithm="HS256")

        with self.assertRaisesRegex(self.module.HandshakeAuthError, "invalid token"):
            self.module.authenticate_ws_handshake(
                {"Sec-WebSocket-Protocol": f"simples.v1,bearer.{token}"},
                {},
                "secret",
            )


class WsEndpointRegistrationTest(unittest.TestCase):
    def test_ws_route_registered(self):
        app_module = WsRunSessionAuthBehaviorTest._load_app_module_with_callable_ws_run()
        app = app_module.app

        rules = {rule.rule for rule in app.url_map.iter_rules()}
        self.assertIn("/ws/run", rules)


class FlaskSockImportGuardTest(unittest.TestCase):
    @staticmethod
    def _load_app_module_raising_on_flask_sock(module_error):
        module_path = ROOT / "backend" / "app.py"
        spec = importlib.util.spec_from_file_location("backend.app_import_guard_test", module_path)
        module = importlib.util.module_from_spec(spec)
        original_import = __import__

        def import_with_flask_sock_failure(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "flask_sock":
                raise module_error
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=import_with_flask_sock_failure):
            spec.loader.exec_module(module)
        return module

    def test_missing_flask_sock_module_is_optional(self):
        app_module = self._load_app_module_raising_on_flask_sock(
            ModuleNotFoundError("No module named 'flask_sock'", name="flask_sock")
        )

        self.assertIsNone(app_module.Sock)

    def test_missing_flask_sock_module_with_missing_exc_name_is_optional(self):
        app_module = self._load_app_module_raising_on_flask_sock(
            ModuleNotFoundError("No module named 'flask_sock'")
        )

        self.assertIsNone(app_module.Sock)

    def test_transitive_module_not_found_error_is_not_swallowed(self):
        with self.assertRaises(ModuleNotFoundError) as context:
            self._load_app_module_raising_on_flask_sock(
                ModuleNotFoundError("No module named 'wsproto'", name="wsproto")
            )

        self.assertEqual(context.exception.name, "wsproto")

    def test_unrelated_missing_module_with_missing_exc_name_is_not_swallowed(self):
        with self.assertRaisesRegex(ModuleNotFoundError, "wsproto") as context:
            self._load_app_module_raising_on_flask_sock(
                ModuleNotFoundError("No module named 'wsproto'")
            )

        self.assertIsNone(context.exception.name)


class FakeWs:
    def __init__(self, incoming=None):
        self._incoming = list(incoming or [])
        self.sent = []
        self.closed_codes = []

    def send(self, payload):
        self.sent.append(payload)

    def receive(self):
        if self._incoming:
            return self._incoming.pop(0)
        return None

    def close(self, code):
        self.closed_codes.append(code)


class FakePopen:
    """Simulates subprocess.Popen for tests. Provides stdout/stdin/wait/kill."""

    def __init__(self, stdout_data: bytes = b"", *, hang: bool = False):
        self._killed = threading.Event()
        self._stdin_data: list[bytes] = []
        self.returncode = 0
        self.kill_calls = 0
        parent = self
        chunks = [stdout_data] if stdout_data else []
        chunks_iter = iter(chunks)

        class _Stdout:
            def read(self, n: int) -> bytes:
                if parent._killed.is_set():
                    return b""
                if hang:
                    parent._killed.wait()
                    return b""
                try:
                    return next(chunks_iter)
                except StopIteration:
                    return b""

        class _Stdin:
            def write(self, data: bytes) -> None:
                parent._stdin_data.append(data)

            def flush(self) -> None:
                pass

        self.stdout = _Stdout()
        self.stdin = _Stdin()

    def wait(self) -> int:
        return self.returncode

    def kill(self) -> None:
        self.kill_calls += 1
        self._killed.set()


class FakeRequest:
    def __init__(self, headers=None, args=None):
        self.headers = headers or {}
        self.args = args or {}


class WsRunSessionAuthBehaviorTest(unittest.TestCase):
    @staticmethod
    def _load_app_module_with_callable_ws_run():
        module_path = ROOT / "backend" / "app.py"
        spec = importlib.util.spec_from_file_location("backend.app_test_double", module_path)
        module = importlib.util.module_from_spec(spec)

        fake_flask_sock = ModuleType("flask_sock")

        class FakeSock:
            def __init__(self, app):
                self.app = app

            def route(self, path):
                def decorator(fn):
                    self.app.add_url_rule(path, endpoint=f"ws_{fn.__name__}", view_func=lambda: "")
                    return fn

                return decorator

        fake_flask_sock.Sock = FakeSock
        with patch.dict(sys.modules, {"flask_sock": fake_flask_sock}):
            spec.loader.exec_module(module)
        return module

    def test_ws_run_closes_with_1008_on_handshake_auth_error(self):
        app_module = self._load_app_module_with_callable_ws_run()
        from backend.ws.handshake import HandshakeAuthError

        ws = FakeWs()
        with patch.object(
            app_module,
            "load_supabase_auth_config",
            return_value=SimpleNamespace(jwt_secret="secret"),
        ), patch.object(
            app_module,
            "handle_run_session",
            side_effect=HandshakeAuthError("invalid token"),
        ):
            app_module.ws_run(ws)

        self.assertEqual(ws.closed_codes, [1008])

    def test_ws_run_closes_with_1011_when_auth_config_is_missing(self):
        app_module = self._load_app_module_with_callable_ws_run()
        ws = FakeWs()

        with patch.object(
            app_module,
            "load_supabase_auth_config",
            side_effect=KeyError("SUPABASE_JWT_SECRET"),
        ), patch.object(app_module, "handle_run_session") as handle_mock:
            app_module.ws_run(ws)

        handle_mock.assert_not_called()
        self.assertEqual(ws.closed_codes, [1011])

    def test_ws_run_closes_with_1011_on_run_session_error(self):
        app_module = self._load_app_module_with_callable_ws_run()
        from backend.ws.run_session import RunSessionError

        ws = FakeWs()
        with patch.object(
            app_module,
            "load_supabase_auth_config",
            return_value=SimpleNamespace(jwt_secret="secret"),
        ), patch.object(
            app_module,
            "handle_run_session",
            side_effect=RunSessionError("runtime failure"),
        ):
            app_module.ws_run(ws)

        self.assertEqual(ws.closed_codes, [1011])

    def test_handle_run_session_sends_session_ready_idle_with_user_id(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"},
            args={},
        )
        ws = FakeWs(incoming=[None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ) as auth_mock:
            run_session_module.handle_run_session(ws, request, "secret")

        auth_mock.assert_called_once_with(request.headers, request.args, "secret")
        self.assertEqual(len(ws.sent), 1)
        payload = json.loads(ws.sent[0])
        self.assertEqual(payload["type"], "session_ready")
        self.assertEqual(payload["state"], "idle")
        self.assertEqual(payload["user_id"], "user-123")

    def test_handle_run_session_bootstrap_payload_shape_regression(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"},
            args={},
        )
        ws = FakeWs(incoming=[None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        payload = json.loads(ws.sent[0])
        self.assertEqual(set(payload.keys()), {"type", "state", "user_id"})
        self.assertTrue(all(isinstance(payload[key], str) for key in payload))

    def test_handle_run_session_ignores_invalid_json_and_missing_type(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"},
            args={},
        )
        ws = FakeWs(incoming=["{bad json", '{"payload":"ok"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        self.assertEqual(len(ws.sent), 1)
        self.assertEqual(json.loads(ws.sent[0])["type"], "session_ready")

    def test_handle_run_session_rejects_missing_token(self):
        import backend.ws.run_session as run_session_module
        from backend.ws.handshake import HandshakeAuthError

        request = FakeRequest(headers={}, args={})
        ws = FakeWs(incoming=[None])

        with self.assertRaisesRegex(HandshakeAuthError, "missing bearer token"):
            run_session_module.handle_run_session(ws, request, "secret")

    def test_handle_run_session_rejects_invalid_token(self):
        import backend.ws.run_session as run_session_module
        from backend.ws.handshake import HandshakeAuthError

        request = FakeRequest(
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.not-a-jwt"},
            args={},
        )
        ws = FakeWs(incoming=[None])

        with self.assertRaisesRegex(HandshakeAuthError, "invalid token"):
            run_session_module.handle_run_session(ws, request, "secret")

    def test_handle_run_session_routes_compile_and_run_through_state_machine(self):
        import backend.ws.run_session as run_session_module

        class TrackingMachine:
            start_compile_calls = 0

            def __init__(self):
                self.state = SimpleNamespace(value="idle")

            def start_compile(self):
                type(self).start_compile_calls += 1
                self.state = SimpleNamespace(value="compiling")
                return True

            def accepts_stdin(self):
                return False

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(run_session_module, "SessionStateMachine", TrackingMachine), patch.object(
            run_session_module, "compile_simples", return_value={"ok": False, "error": "stub"}
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertEqual(sent[0]["type"], "session_ready")
        self.assertEqual(sent[1]["type"], "compile_started")
        self.assertEqual(sent[1]["state"], "compiling")
        self.assertEqual(TrackingMachine.start_compile_calls, 1)

    def test_handle_run_session_routes_ping_and_ignores_non_executing_stdin(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(
            incoming=[
                '{"type":"stdin","data":"hello"}',
                '{"type":"ping","nonce":"n1"}',
                None,
            ]
        )

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertEqual(sent[0]["type"], "session_ready")
        self.assertEqual(sent[1]["type"], "invalid_state")
        self.assertEqual(sent[1]["command"], "stdin")
        self.assertEqual(sent[2], {"type": "pong", "nonce": "n1"})

    def test_handle_run_session_ignores_unexpected_messages_without_crash(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(
            incoming=[
                '{"type":"unknown"}',
                "[]",
                '{"type":"compile_and_run","extra":1}',
                '{"type":"invalid"}',
                None,
            ]
        )

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": False, "error": "stub"}
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertEqual(sent[0]["type"], "session_ready")
        self.assertEqual(sent[1]["type"], "compile_started")

    def test_handle_run_session_forwards_stdout_and_relays_stdin(self):
        import backend.ws.run_session as run_session_module

        fake_proc = FakePopen(stdout_data=b"prompt> ")

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', '{"type":"stdin","data":"42\\n"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", return_value=b"ELF"
        ), patch.object(
            run_session_module.subprocess, "Popen", return_value=fake_proc
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertIn({"type": "stdout", "data": "prompt> "}, sent)

    def test_handle_run_session_stdin_in_invalid_state_returns_safe_message(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"stdin","data":"ignored"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertEqual(sent[1]["type"], "invalid_state")
        self.assertEqual(sent[1]["command"], "stdin")
        self.assertEqual(sent[1]["state"], "idle")

    def test_handle_run_session_emits_compile_protocol_sequence(self):
        import backend.ws.run_session as run_session_module

        fake_proc = FakePopen(stdout_data=b"ok\n")

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", return_value=b"ELF"
        ), patch.object(
            run_session_module.subprocess, "Popen", return_value=fake_proc
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        event_types = [item["type"] for item in sent]
        self.assertIn("compile_started", event_types)
        self.assertIn("asm_generated", event_types)
        self.assertIn("exec_started", event_types)
        self.assertIn("stdout", event_types)

    def test_handle_run_session_stop_and_ping_keep_connection_alive(self):
        import backend.ws.run_session as run_session_module

        fake_proc = FakePopen()  # no stdout, exits immediately

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', '{"type":"stop"}', '{"type":"ping","nonce":"n2"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", return_value=b"ELF"
        ), patch.object(
            run_session_module.subprocess, "Popen", return_value=fake_proc
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        event_types = [item["type"] for item in sent]
        self.assertIn("exit", event_types)
        self.assertIn("pong", event_types)

    def test_handle_run_session_emits_structured_json_logs_for_execution(self):
        import backend.ws.run_session as run_session_module

        fake_proc = FakePopen()  # no stdout, exits immediately

        request = FakeRequest(
            headers={
                "Sec-WebSocket-Protocol": "simples.v1,bearer.token",
                "X-Request-ID": "req-123",
                "X-Real-IP": "203.0.113.42",
            },
            args={},
        )
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', None])
        buffer = io.StringIO()

        with redirect_stdout(buffer), patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", return_value=b"ELF"
        ), patch.object(
            run_session_module.subprocess, "Popen", return_value=fake_proc
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        logs = [json.loads(line) for line in buffer.getvalue().splitlines() if line.strip()]
        event_names = [item["event"] for item in logs]
        self.assertIn("execution_started", event_names)
        self.assertIn("execution_finished", event_names)
        finished = next(item for item in logs if item["event"] == "execution_finished")
        self.assertEqual(finished["logger"], "simples.executor")
        self.assertEqual(finished["user_id"], "user-123")
        self.assertEqual(finished["request_id"], "req-123")
        self.assertEqual(finished["client_ip"], "203.0.113.42")
        self.assertEqual(finished["exit_code"], 0)
        self.assertIn("duration_ms", finished)

    def test_handle_run_session_bootstrap_error_emits_runtime_error_event(self):
        import backend.ws.run_session as run_session_module
        from backend.ws.execution import ExecutionStrategyError

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=['{"type":"compile_and_run"}', None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", side_effect=ExecutionStrategyError("boom")
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertIn("runtime_error", [item["type"] for item in sent])

    def test_handle_run_session_returns_rate_limited_event_before_session_ready(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = FakeWs(incoming=[None])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "allow_execution_request", return_value=(False, 19)
        ):
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertEqual(sent[0]["type"], "rate_limited")
        self.assertEqual(sent[0]["scope"], "execution")
        self.assertEqual(sent[0]["retry_after"], 19)
        self.assertEqual(len(sent), 1)

    def test_handle_run_session_triggers_wall_clock_timeout(self):
        import backend.ws.run_session as run_session_module

        fake_proc = FakePopen(hang=True)  # blocks stdout until killed

        class SlowWs(FakeWs):
            def receive(self):
                if self._incoming:
                    item = self._incoming.pop(0)
                    if item == "__pause__":
                        import time

                        time.sleep(0.05)
                        return None
                    return item
                return None

        request = FakeRequest(headers={"Sec-WebSocket-Protocol": "simples.v1,bearer.token"}, args={})
        ws = SlowWs(incoming=['{"type":"compile_and_run"}', "__pause__"])

        with patch.object(
            run_session_module, "authenticate_ws_handshake", return_value="user-123"
        ), patch.object(
            run_session_module, "compile_simples", return_value={"ok": True, "nasm": "; stub\n"}
        ), patch.object(
            run_session_module, "_build_binary", return_value=b"ELF"
        ), patch.object(
            run_session_module.subprocess, "Popen", return_value=fake_proc
        ):
            run_session_module.EXECUTION_TIMEOUT = 0.01
            run_session_module.handle_run_session(ws, request, "secret")

        sent = [json.loads(item) for item in ws.sent]
        self.assertIn("timeout", [item["type"] for item in sent])
        self.assertGreaterEqual(fake_proc.kill_calls, 1)


if __name__ == "__main__":
    unittest.main()

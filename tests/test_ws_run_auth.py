import importlib.util
import json
import pathlib
import sys
import unittest
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

    def test_extracts_subprotocol_bearer_token(self):
        headers = {"Sec-WebSocket-Protocol": "simples.v1,bearer,token-123"}

        token = self.module.extract_token_from_handshake(headers, {})

        self.assertEqual(token, "token-123")

    def test_extracts_subprotocol_bearer_dot_token(self):
        headers = {"Sec-WebSocket-Protocol": "simples.v1,bearer.token-abc"}

        token = self.module.extract_token_from_handshake(headers, {})

        self.assertEqual(token, "token-abc")

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
            {"Sec-WebSocket-Protocol": f"simples.v1,bearer,{token}"},
            {},
            "secret",
        )

        self.assertEqual(user_id, "user-123")

    def test_authenticate_ws_handshake_wraps_auth_error(self):
        with self.assertRaisesRegex(self.module.HandshakeAuthError, "invalid token"):
            self.module.authenticate_ws_handshake(
                {"Sec-WebSocket-Protocol": "simples.v1,bearer,not-a-jwt"},
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

    def test_handle_run_session_sends_session_ready_idle_with_user_id(self):
        import backend.ws.run_session as run_session_module

        request = FakeRequest(
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer,token"},
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
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer,token"},
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
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer,token"},
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
            headers={"Sec-WebSocket-Protocol": "simples.v1,bearer,not-a-jwt"},
            args={},
        )
        ws = FakeWs(incoming=[None])

        with self.assertRaisesRegex(HandshakeAuthError, "invalid token"):
            run_session_module.handle_run_session(ws, request, "secret")


if __name__ == "__main__":
    unittest.main()

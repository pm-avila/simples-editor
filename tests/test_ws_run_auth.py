import importlib.util
import pathlib
import unittest

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
        from backend.app import app

        rules = {rule.rule for rule in app.url_map.iter_rules()}
        self.assertIn("/ws/run", rules)


if __name__ == "__main__":
    unittest.main()

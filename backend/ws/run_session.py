import json

from backend.ws.handshake import authenticate_ws_handshake
from backend.ws.state_machine import SessionStateMachine


class RunSessionError(Exception):
    """Raised when run session processing fails unexpectedly."""


def _send_json(ws, payload):
    ws.send(json.dumps(payload))


def handle_run_session(ws, request, jwt_secret):
    user_id = authenticate_ws_handshake(request.headers, request.args, jwt_secret)
    machine = SessionStateMachine()
    try:
        _send_json(
            ws,
            {
                "type": "session_ready",
                "state": machine.state.value,
                "user_id": user_id,
            },
        )

        while True:
            raw = ws.receive()
            if raw is None:
                break
            if not isinstance(raw, str):
                continue
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(message, dict):
                continue

            message_type = message.get("type")
            if message_type == "compile_and_run":
                if machine.start_compile():
                    _send_json(
                        ws,
                        {
                            "type": "compile_started",
                            "state": machine.state.value,
                        },
                    )
                continue

            if message_type == "ping":
                payload = {"type": "pong"}
                if "nonce" in message:
                    payload["nonce"] = message["nonce"]
                _send_json(ws, payload)
                continue

            if message_type == "stdin":
                if not machine.accepts_stdin():
                    continue
                continue
    except Exception as exc:
        raise RunSessionError("run session failed") from exc

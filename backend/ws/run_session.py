import json

from backend.ws.handshake import authenticate_ws_handshake
from backend.ws.state_machine import SessionStateMachine


def handle_run_session(ws, request, jwt_secret):
    user_id = authenticate_ws_handshake(request.headers, request.args, jwt_secret)
    machine = SessionStateMachine()
    ws.send(
        json.dumps(
            {
                "type": "session_ready",
                "state": machine.state.value,
                "user_id": user_id,
            }
        )
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
        if "type" not in message:
            continue

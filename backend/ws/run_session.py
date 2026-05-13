import json
import os

from backend.ws.handshake import authenticate_ws_handshake
from backend.ws.execution import ExecutionStrategyError
from backend.ws.pty_execution import PtyExecutionStrategy
from backend.ws.state_machine import SessionStateMachine


class RunSessionError(Exception):
    """Raised when run session processing fails unexpectedly."""


def _send_json(ws, payload):
    ws.send(json.dumps(payload))


def handle_run_session(ws, request, jwt_secret):
    user_id = authenticate_ws_handshake(request.headers, request.args, jwt_secret)
    machine = SessionStateMachine()
    execution = None
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
                    try:
                        execution = PtyExecutionStrategy()
                        sandbox_image = os.environ.get("SANDBOX_IMAGE", "simples-runner:dev")
                        execution.start(image=sandbox_image, command=["/bin/sh"])
                        machine.start_exec()
                        stdout = execution.poll_stdout()
                        if stdout:
                            _send_json(ws, {"type": "stdout", "data": stdout})
                    except ExecutionStrategyError:
                        _send_json(
                            ws,
                            {"type": "runtime_error", "message": "execution bootstrap failed"},
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
                    _send_json(
                        ws,
                        {
                            "type": "invalid_state",
                            "command": "stdin",
                            "state": machine.state.value,
                        },
                    )
                    continue
                try:
                    if execution is not None:
                        execution.send_stdin(message.get("data", ""))
                except ExecutionStrategyError:
                    _send_json(
                        ws,
                        {"type": "runtime_error", "message": "stdin relay failed"},
                    )
                continue
    except Exception as exc:
        raise RunSessionError("run session failed") from exc

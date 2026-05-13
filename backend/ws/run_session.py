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

    def reset_to_idle():
        if hasattr(machine, "reset_idle"):
            machine.reset_idle()

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
                if not machine.start_compile():
                    _send_json(
                        ws,
                        {
                            "type": "invalid_state",
                            "command": "compile_and_run",
                            "state": machine.state.value,
                        },
                    )
                    continue
                _send_json(
                    ws,
                    {
                        "type": "compile_started",
                        "state": machine.state.value,
                    },
                )
                _send_json(ws, {"type": "asm_generated"})
                try:
                    execution = PtyExecutionStrategy()
                    sandbox_image = os.environ.get("SANDBOX_IMAGE", "simples-runner:dev")
                    execution.start(image=sandbox_image, command=["/bin/sh"])
                    can_start_exec = hasattr(machine, "start_exec")
                    if can_start_exec and machine.start_exec():
                        _send_json(ws, {"type": "exec_started", "state": machine.state.value})
                    stdout = execution.poll_stdout()
                    if stdout:
                        _send_json(ws, {"type": "stdout", "data": stdout})
                except ExecutionStrategyError:
                    reset_to_idle()
                    _send_json(ws, {"type": "timeout"})
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

            if message_type == "stop":
                if not machine.accepts_stdin():
                    _send_json(
                        ws,
                        {
                            "type": "invalid_state",
                            "command": "stop",
                            "state": machine.state.value,
                        },
                    )
                    continue
                try:
                    if execution is not None:
                        execution.stop()
                    reset_to_idle()
                    _send_json(ws, {"type": "exit", "exit_code": 0})
                except ExecutionStrategyError:
                    _send_json(
                        ws,
                        {"type": "runtime_error", "message": "stop failed"},
                    )
                continue
    except Exception as exc:
        raise RunSessionError("run session failed") from exc

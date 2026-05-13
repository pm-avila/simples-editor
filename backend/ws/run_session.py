import json
import os
import time
import threading
import uuid

from backend.observability import log_event
from backend.metrics import METRICS
from backend.ws.handshake import authenticate_ws_handshake
from backend.ws.execution import ExecutionStrategyError
from backend.ws.pty_execution import PtyExecutionStrategy
from backend.rate_limit import allow_execution_request
from backend.ws.state_machine import SessionStateMachine


class RunSessionError(Exception):
    """Raised when run session processing fails unexpectedly."""


def _parse_timeout(value: str, default: int = 10) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


EXECUTION_TIMEOUT = _parse_timeout(os.environ.get("EXECUTION_TIMEOUT", "10"))


def _send_json(ws, payload):
    ws.send(json.dumps(payload))


def _client_ip(request):
    forwarded = request.headers.get("X-Real-IP", "") or request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return getattr(request, "remote_addr", None) or "unknown"


def handle_run_session(ws, request, jwt_secret):
    user_id = authenticate_ws_handshake(request.headers, request.args, jwt_secret)
    request_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Request-Id")
        or uuid.uuid4().hex
    )
    allowed, retry_after = allow_execution_request(user_id, _client_ip(request))
    if not allowed:
        _send_json(
            ws,
            {"type": "rate_limited", "scope": "execution", "retry_after": retry_after},
        )
        log_event(
            "simples.executor",
            "execution_rate_limited",
            user_id=user_id,
            request_id=request_id,
            client_ip=_client_ip(request),
            retry_after=retry_after,
        )
        return
    machine = SessionStateMachine()
    execution = None
    timeout_timer = None
    session_closed = False
    execution_started_at = None
    state_lock = threading.Lock()

    def reset_to_idle():
        nonlocal execution, timeout_timer, session_closed
        with state_lock:
            session_closed = True
            current_timer = timeout_timer
            timeout_timer = None
            execution = None
        if hasattr(machine, "reset_idle"):
            machine.reset_idle()
        if current_timer is not None:
            current_timer.cancel()

    def claim_execution():
        nonlocal session_closed
        with state_lock:
            if session_closed:
                return False
            session_closed = True
            return True

    def schedule_timeout():
        nonlocal timeout_timer, execution_started_at

        def on_timeout():
            if not claim_execution():
                return
            current_execution = execution
            duration_ms = None
            if execution_started_at is not None:
                duration_ms = int((time.monotonic() - execution_started_at) * 1000)
            try:
                if current_execution is not None:
                    current_execution.stop()
            except ExecutionStrategyError:
                _send_json(ws, {"type": "runtime_error", "message": "timeout stop failed"})
            reset_to_idle()
            if duration_ms is not None:
                METRICS.observe_execution("timeout", duration_ms / 1000.0)
            else:
                METRICS.observe_execution("timeout", 0.0)
            METRICS.execution_finished()
            log_event(
                "simples.executor",
                "execution_timeout",
                user_id=user_id,
                request_id=request_id,
                client_ip=_client_ip(request),
                duration_ms=duration_ms,
            )
            _send_json(ws, {"type": "timeout"})

        timeout_timer = threading.Timer(EXECUTION_TIMEOUT, on_timeout)
        timeout_timer.daemon = True
        timeout_timer.start()

    METRICS.websocket_connected()
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
                    with state_lock:
                        session_closed = False
                    execution = PtyExecutionStrategy()
                    sandbox_image = os.environ.get("SANDBOX_IMAGE", "simples-runner:dev")
                    execution.start(image=sandbox_image, command=["/bin/sh"])
                    can_start_exec = hasattr(machine, "start_exec")
                    if can_start_exec and machine.start_exec():
                        _send_json(ws, {"type": "exec_started", "state": machine.state.value})
                        execution_started_at = time.monotonic()
                        METRICS.execution_started()
                        log_event(
                            "simples.executor",
                            "execution_started",
                            user_id=user_id,
                            request_id=request_id,
                            client_ip=_client_ip(request),
                        )
                        schedule_timeout()
                    try:
                        stdout = execution.poll_stdout()
                    except ExecutionStrategyError:
                        if not session_closed:
                            reset_to_idle()
                            _send_json(ws, {"type": "timeout"})
                        continue
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
                if not claim_execution():
                    continue
                try:
                    if execution is not None:
                        execution.stop()
                except ExecutionStrategyError:
                    reset_to_idle()
                    _send_json(
                        ws,
                        {"type": "runtime_error", "message": "stop failed"},
                    )
                    continue
                reset_to_idle()
                duration_ms = None
                if execution_started_at is not None:
                    duration_ms = int((time.monotonic() - execution_started_at) * 1000)
                    METRICS.observe_execution("success", duration_ms / 1000.0)
                else:
                    METRICS.observe_execution("success", 0.0)
                METRICS.execution_finished()
                log_event(
                    "simples.executor",
                    "execution_finished",
                    user_id=user_id,
                    request_id=request_id,
                    client_ip=_client_ip(request),
                    duration_ms=duration_ms,
                    exit_code=0,
                )
                _send_json(ws, {"type": "exit", "exit_code": 0})
                continue
    except Exception as exc:
        raise RunSessionError("run session failed") from exc
    finally:
        if timeout_timer is not None:
            timeout_timer.cancel()
        METRICS.websocket_disconnected()

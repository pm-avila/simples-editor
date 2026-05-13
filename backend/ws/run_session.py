import json
import os
import queue
import subprocess
import tempfile
import threading
import time
import uuid

from backend.compiler import compile_simples
from backend.observability import log_event
from backend.metrics import METRICS
from backend.ws.handshake import authenticate_ws_handshake
from backend.ws.execution import ExecutionStrategyError
from backend.ws.pty_execution import PtyExecutionStrategy
from backend.rate_limit import allow_execution_request
from backend.ws.state_machine import SessionStateMachine


NASM_BIN = os.environ.get("NASM_BIN", "nasm")
LD_BIN = os.environ.get("LD_BIN", "i686-linux-gnu-ld")
ASSEMBLE_TIMEOUT = 10


def _build_binary(nasm_source: str) -> bytes:
    """Assemble NASM source to 32-bit ELF binary. Returns raw binary bytes."""
    with tempfile.TemporaryDirectory(prefix="simples-exec-") as d:
        asm_path = os.path.join(d, "prog.asm")
        obj_path = os.path.join(d, "prog.o")
        bin_path = os.path.join(d, "prog")
        with open(asm_path, "w", encoding="utf-8") as f:
            f.write(nasm_source)
        r = subprocess.run(
            [NASM_BIN, "-f", "elf32", asm_path, "-o", obj_path],
            capture_output=True,
            timeout=ASSEMBLE_TIMEOUT,
        )
        if r.returncode != 0:
            raise ExecutionStrategyError(
                f"assembly failed: {r.stderr.decode('utf-8', errors='replace').strip()}"
            )
        r = subprocess.run(
            [LD_BIN, "-o", bin_path, obj_path],
            capture_output=True,
            timeout=ASSEMBLE_TIMEOUT,
        )
        if r.returncode != 0:
            raise ExecutionStrategyError(
                f"linking failed: {r.stderr.decode('utf-8', errors='replace').strip()}"
            )
        os.chmod(bin_path, 0o755)
        with open(bin_path, "rb") as f:
            return f.read()

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

    # Background thread drains ws.receive() into a queue so the execution
    # loop and the main message loop can both be driven from the same source.
    internal_ws_q: queue.Queue[str | None] = queue.Queue()

    def _ws_reader() -> None:
        while True:
            raw = ws.receive()
            internal_ws_q.put(raw)
            if raw is None:
                break

    threading.Thread(target=_ws_reader, daemon=True).start()

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
                if current_execution is not None and hasattr(current_execution, "kill"):
                    current_execution.kill()
            except OSError:
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

    def _relay_ws_msg_during_exec(msg: dict, proc: subprocess.Popen) -> None:
        """Handle a WS message that arrived while execution is active."""
        msg_type = msg.get("type")
        if msg_type == "stdin" and machine.accepts_stdin():
            data = msg.get("data", "")
            try:
                if proc.stdin is not None:
                    proc.stdin.write(data.encode("utf-8") if isinstance(data, str) else data)
                    proc.stdin.flush()
            except OSError:
                _send_json(ws, {"type": "runtime_error", "message": "stdin relay failed"})
        elif msg_type == "stop" and machine.accepts_stdin():
            try:
                proc.kill()
            except OSError:
                pass
        elif msg_type == "ping":
            payload: dict = {"type": "pong"}
            if "nonce" in msg:
                payload["nonce"] = msg["nonce"]
            _send_json(ws, payload)

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
            raw = internal_ws_q.get()
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
                _send_json(ws, {"type": "compile_started", "state": machine.state.value})

                code = message.get("code", "")
                compile_result = compile_simples(code)
                if not compile_result["ok"]:
                    if hasattr(machine, "reset_idle"):
                        machine.reset_idle()
                    _send_json(ws, {"type": "compile_error", "error": compile_result["error"]})
                    continue

                _send_json(ws, {"type": "asm_generated", "nasm": compile_result["nasm"]})

                try:
                    binary_bytes = _build_binary(compile_result["nasm"])
                except ExecutionStrategyError as exc:
                    if hasattr(machine, "reset_idle"):
                        machine.reset_idle()
                    _send_json(ws, {"type": "runtime_error", "message": str(exc)})
                    continue

                if not (hasattr(machine, "start_exec") and machine.start_exec()):
                    continue

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

                with state_lock:
                    session_closed = False

                # Write binary to temp file and execute it
                tmpdir_obj = tempfile.mkdtemp(prefix="simples-run-")
                bin_path = os.path.join(tmpdir_obj, "prog")
                with open(bin_path, "wb") as f:
                    f.write(binary_bytes)
                os.chmod(bin_path, 0o755)

                proc = subprocess.Popen(
                    [bin_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                )
                with state_lock:
                    execution = proc

                schedule_timeout()

                # Stream stdout in a background thread via queue
                stdout_q: queue.Queue[bytes | None] = queue.Queue()

                def _read_stdout(p: subprocess.Popen, q: "queue.Queue[bytes | None]") -> None:
                    try:
                        assert p.stdout is not None
                        for chunk in iter(lambda: p.stdout.read(256), b""):
                            q.put(chunk)
                    finally:
                        q.put(None)

                threading.Thread(target=_read_stdout, args=(proc, stdout_q), daemon=True).start()

                # Inner event loop: interleave stdout chunks with incoming WS
                # messages (stdin, stop, ping) until the process exits.
                while True:
                    # Non-blocking check for a pending WS message from client.
                    try:
                        ws_raw = internal_ws_q.get_nowait()
                        if ws_raw is None:
                            # WS closed mid-execution — kill process.
                            internal_ws_q.put(None)  # re-enqueue for outer loop
                            try:
                                proc.kill()
                            except OSError:
                                pass
                            # fall through: stdout_q will drain, then EOF
                        else:
                            try:
                                ws_msg = json.loads(ws_raw)
                                if isinstance(ws_msg, dict):
                                    _relay_ws_msg_during_exec(ws_msg, proc)
                            except json.JSONDecodeError:
                                pass
                    except queue.Empty:
                        pass

                    # Wait briefly for stdout output.
                    try:
                        chunk = stdout_q.get(timeout=0.05)
                    except queue.Empty:
                        continue

                    if chunk is None:
                        break  # stdout EOF — process has exited
                    if chunk:
                        _send_json(ws, {"type": "stdout", "data": chunk.decode("utf-8", errors="replace")})

                proc.wait()
                exit_code = proc.returncode if proc.returncode is not None else 0
                import shutil
                shutil.rmtree(tmpdir_obj, ignore_errors=True)

                if claim_execution():
                    reset_to_idle()
                    duration_ms = int((time.monotonic() - execution_started_at) * 1000)
                    METRICS.observe_execution("success", duration_ms / 1000.0)
                    METRICS.execution_finished()
                    log_event(
                        "simples.executor",
                        "execution_finished",
                        user_id=user_id,
                        request_id=request_id,
                        client_ip=_client_ip(request),
                        duration_ms=duration_ms,
                        exit_code=exit_code,
                    )
                    _send_json(ws, {"type": "exit", "exit_code": exit_code})
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

    except Exception as exc:
        raise RunSessionError("run session failed") from exc
    finally:
        if timeout_timer is not None:
            timeout_timer.cancel()
        METRICS.websocket_disconnected()


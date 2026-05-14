from flask import Flask, jsonify, request
import time
import uuid
from flask import Response


def _is_optional_flask_sock_import_error(exc):
    if exc.name == "flask_sock":
        return True

    if exc.name is not None:
        return False

    return "No module named" in str(exc) and "'flask_sock'" in str(exc)


try:
    from flask_sock import Sock
except ModuleNotFoundError as exc:
    if not _is_optional_flask_sock_import_error(exc):
        raise
    Sock = None

from backend.auth_config import load_supabase_auth_config
from backend.compiler import compile_simples
from backend.health import build_health_payload
from backend.observability import log_event
from backend.metrics import METRICS
from backend.metrics import render_metrics
from backend.rate_limit import allow_compile_request
from backend.ws.handshake import HandshakeAuthError
from backend.ws.run_session import handle_run_session
from backend.ws.run_session import RunSessionError


app = Flask(__name__)
sock = Sock(app) if Sock is not None else None


def _client_ip(request):
    forwarded = request.headers.get("X-Real-IP", "") or request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


@app.route("/")
def index():
    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/health")
def api_health():
    return jsonify(build_health_payload())


@app.post("/api/compile")
def api_compile():
    request_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Request-Id")
        or uuid.uuid4().hex
    )
    start_time = time.monotonic()
    allowed, retry_after = allow_compile_request(_client_ip(request))
    if not allowed:
        log_event(
            "simples.compiler",
            "compile_rate_limited",
            request_id=request_id,
            client_ip=_client_ip(request),
            retry_after=retry_after,
        )
        return (
            jsonify(
                {
                    "error": {
                        "phase": "compile",
                        "line": 0,
                        "column": 0,
                        "message": "rate limit exceeded",
                        "retry_after": retry_after,
                    }
                }
            ),
            429,
        )

    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code or not code.strip():
        return jsonify({"error": "código vazio"}), 400

    result = compile_simples(code)
    duration_ms = int((time.monotonic() - start_time) * 1000)
    if result["ok"]:
        METRICS.observe_compile("nasm", duration_ms / 1000.0)
        log_event(
            "simples.compiler",
            "compile_finished",
            request_id=request_id,
            client_ip=_client_ip(request),
            duration_ms=duration_ms,
            ok=True,
        )
        return jsonify({"nasm": result["nasm"]}), 200
    METRICS.observe_compile(result["error"]["phase"], duration_ms / 1000.0)
    METRICS.increment_compile_error(result["error"]["phase"])
    log_event(
        "simples.compiler",
        "compile_finished",
        request_id=request_id,
        client_ip=_client_ip(request),
        duration_ms=duration_ms,
        ok=False,
    )
    return jsonify({"error": result["error"]}), 422


@app.get("/metrics")
def metrics():
    return Response(render_metrics(), mimetype="text/plain; version=0.0.4; charset=utf-8")


if sock is not None:

    @sock.route("/ws/run")
    def ws_run(ws):
        try:
            auth = load_supabase_auth_config()
        except (KeyError, ValueError):
            ws.close(1011)
            return
        try:
            handle_run_session(ws, request, auth.jwt_secret, supabase_url=auth.url)
        except HandshakeAuthError:
            ws.close(1008)
        except RunSessionError:
            ws.close(1011)


def create_app():
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

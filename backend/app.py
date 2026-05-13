from flask import Flask, jsonify, request
try:
    from flask_sock import Sock
except ModuleNotFoundError as exc:
    if exc.name != "flask_sock":
        raise
    Sock = None

from backend.auth_config import load_supabase_auth_config
from backend.compiler import compile_simples
from backend.health import build_health_payload
from backend.ws.handshake import HandshakeAuthError
from backend.ws.run_session import handle_run_session


app = Flask(__name__)
sock = Sock(app) if Sock is not None else None


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
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code or not code.strip():
        return jsonify({"error": "código vazio"}), 400

    result = compile_simples(code)
    if result["ok"]:
        return jsonify({"nasm": result["nasm"]}), 200
    return jsonify({"error": result["error"]}), 422


if sock is not None:

    @sock.route("/ws/run")
    def ws_run(ws):
        try:
            auth = load_supabase_auth_config()
        except (KeyError, ValueError):
            ws.close(1011)
            return
        try:
            handle_run_session(ws, request, auth.jwt_secret)
        except HandshakeAuthError:
            ws.close(1008)


def create_app():
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

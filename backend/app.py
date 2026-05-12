from flask import Flask, jsonify, request

from backend.compiler import compile_simples
from backend.health import build_health_payload


app = Flask(__name__)


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


def create_app():
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify

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


def create_app():
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

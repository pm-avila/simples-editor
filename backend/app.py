from flask import Flask, jsonify

from backend.health import build_health_payload


def create_app():
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        return jsonify(build_health_payload())

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

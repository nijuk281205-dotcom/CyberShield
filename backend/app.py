import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

from config import Config
from database import db
from routes.api import api

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cybershield")


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    CORS(app, origins=app.config["CORS_ORIGINS"], methods=["GET", "POST", "DELETE", "OPTIONS"])
    Limiter(get_remote_address, app=app, default_limits=[app.config["RATE_LIMIT"]], storage_uri="memory://")

    db.init_db(app.config["DATABASE_PATH"])
    app.register_blueprint(api)

    @app.after_request
    def secure_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify({"error": e.description or e.name}), e.code

    @app.errorhandler(Exception)
    def server_error(e):
        log.exception("Unhandled error")
        return jsonify({"error": "Something went wrong on the server."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

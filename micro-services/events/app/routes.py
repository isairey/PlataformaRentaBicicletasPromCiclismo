from flask import Blueprint, jsonify

from .views.competitions import competitions_bp
from .views.events import events_bp
from .views.routes import routes_bp


def register_blueprints(app):
    api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")
    api_v1.register_blueprint(competitions_bp)
    api_v1.register_blueprint(events_bp)
    api_v1.register_blueprint(routes_bp)
    app.register_blueprint(api_v1)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

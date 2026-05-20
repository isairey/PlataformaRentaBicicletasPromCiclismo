from flask import Blueprint, jsonify

from app.auth import require_authentication

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/v1/health", methods=["GET"])
@require_authentication
def health():
    return jsonify({"status": "ok"}), 200

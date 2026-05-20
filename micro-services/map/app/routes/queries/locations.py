from flask import Blueprint, jsonify

from app.auth import require_authentication
from app.repositories.location_repository import LocationRepository
from app.services.location_service import LocationService

locations_queries_bp = Blueprint("queries_locations", __name__)


def _get_service() -> LocationService:
    return LocationService(LocationRepository())


@locations_queries_bp.route("/api/v1/locations/available", methods=["GET"])
@require_authentication
def list_available_locations():
    service = _get_service()
    items = service.list_available_for_map()
    return jsonify([i.model_dump(mode="json", by_alias=True) for i in items]), 200

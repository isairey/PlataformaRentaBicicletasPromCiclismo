from flask import Blueprint, jsonify, request

from app.auth import require_authentication
from app.models.bike import BikeState, BikeType
from app.repositories.bike_repository import BikeRepository
from app.services.bike_service import BikeService
from app.utils.pagination import parse_pagination

queries_bp = Blueprint("queries_bikes", __name__)


def _get_service() -> BikeService:
    return BikeService(BikeRepository())


@queries_bp.route("/api/v1/bikes", methods=["GET"])
@require_authentication
def list_bikes():
    page, page_size, _ = parse_pagination(request.args)

    state_str = request.args.get("state")
    type_str = request.args.get("type")

    state = None
    if state_str:
        try:
            state = BikeState(state_str)
        except ValueError:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": f"Invalid value for filter 'state'.",
                "details": {"field": "state", "value": state_str, "accepted": [s.value for s in BikeState]},
            }), 422

    bike_type = None
    if type_str:
        try:
            bike_type = BikeType(type_str)
        except ValueError:
            return jsonify({
                "code": "VALIDATION_ERROR",
                "message": f"Invalid value for filter 'type'.",
                "details": {"field": "type", "value": type_str, "accepted": [t.value for t in BikeType]},
            }), 422

    service = _get_service()
    response = service.list_bikes(state=state, bike_type=bike_type, page=page, page_size=page_size)
    return jsonify(response.model_dump(mode="json")), 200


@queries_bp.route("/api/v1/bikes/<string:id>", methods=["GET"])
@require_authentication
def get_bike(id):
    service = _get_service()
    response = service.get_bike(id)
    return jsonify(response.model_dump(mode="json")), 200

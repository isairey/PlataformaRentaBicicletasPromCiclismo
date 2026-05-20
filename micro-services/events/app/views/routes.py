from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.auth import require_admin, require_authentication
from app.extensions import db
from app.models import Route

routes_bp = Blueprint("routes", __name__, url_prefix="/events")

REQUIRED_FIELDS = {"name", "distance", "difficulty", "description"}


def _validate_payload(payload: dict) -> dict:
    missing_fields = sorted(field for field in REQUIRED_FIELDS if payload.get(field) in (None, ""))
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"Missing required fields: {missing}")

    try:
        distance = float(payload["distance"])
    except (TypeError, ValueError) as exc:
        raise ValueError("'distance' must be a valid number") from exc

    if distance <= 0:
        raise ValueError("'distance' must be greater than 0")

    coordinates = payload.get("coordinates")
    if coordinates is not None and not isinstance(coordinates, (list, dict)):
        raise ValueError("'coordinates' must be a valid JSON array or object")

    return {
        "name": str(payload["name"]).strip(),
        "distance": distance,
        "difficulty": str(payload["difficulty"]).strip(),
        "description": str(payload["description"]).strip(),
        "coordinates": coordinates,
    }


@routes_bp.post("/routes")
@require_admin
def create_route():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    route = Route(**validated_payload)

    try:
        db.session.add(route)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not save route"}), 500

    return jsonify(route.to_dict()), 201


@routes_bp.put("/routes/<int:route_id>")
@require_admin
def update_route(route_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    route = db.session.get(Route, route_id)
    if route is None:
        abort(404, description="Route not found")

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    for field_name, field_value in validated_payload.items():
        setattr(route, field_name, field_value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not update route"}), 500

    return jsonify(route.to_dict()), 200


@routes_bp.delete("/routes/<int:route_id>")
@require_admin
def delete_route(route_id: int):
    route = db.session.get(Route, route_id)
    if route is None:
        abort(404, description="Route not found")

    try:
        db.session.delete(route)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not delete route"}), 500

    return jsonify({"message": "Route deleted successfully"}), 200


@routes_bp.get("/routes")
@require_authentication
def list_routes():
    routes = Route.query.order_by(Route.name.asc()).all()
    return jsonify([route.to_dict() for route in routes]), 200

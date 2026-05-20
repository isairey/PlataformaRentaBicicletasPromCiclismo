from datetime import date

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.auth import require_admin, require_authentication
from app.extensions import db
from app.models import Competition

competitions_bp = Blueprint("competitions", __name__, url_prefix="/events")

REQUIRED_FIELDS = {"name", "startDate", "endDate", "description", "type"}


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"'{field_name}' must be a valid ISO date (YYYY-MM-DD)") from exc


def _validate_payload(payload: dict) -> dict:
    missing_fields = sorted(field for field in REQUIRED_FIELDS if not payload.get(field))
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"Missing required fields: {missing}")

    start_date = _parse_iso_date(payload["startDate"], "startDate")
    end_date = _parse_iso_date(payload["endDate"], "endDate")

    if end_date <= start_date:
        raise ValueError("'endDate' must be after 'startDate'")

    return {
        "name": payload["name"].strip(),
        "start_date": start_date,
        "end_date": end_date,
        "description": payload["description"].strip(),
        "type": payload["type"].strip(),
    }


@competitions_bp.post("/competitions")
@require_admin
def create_competition():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    competition = Competition(**validated_payload)

    try:
        db.session.add(competition)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not save competition"}), 500

    return jsonify(competition.to_dict()), 201


@competitions_bp.put("/competitions/<int:competition_id>")
@require_admin
def update_competition(competition_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    competition = db.session.get(Competition, competition_id)
    if competition is None:
        abort(404, description="Competition not found")

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    for field_name, field_value in validated_payload.items():
        setattr(competition, field_name, field_value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not update competition"}), 500

    return jsonify(competition.to_dict()), 200


@competitions_bp.delete("/competitions/<int:competition_id>")
@require_admin
def delete_competition(competition_id: int):
    competition = db.session.get(Competition, competition_id)
    if competition is None:
        abort(404, description="Competition not found")

    try:
        db.session.delete(competition)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not delete competition"}), 500

    return jsonify({"message": "Competition deleted successfully"}), 200


@competitions_bp.get("/competitions")
@require_authentication
def list_competitions():
    competitions = Competition.query.order_by(Competition.start_date.asc()).all()
    return jsonify([competition.to_dict() for competition in competitions]), 200

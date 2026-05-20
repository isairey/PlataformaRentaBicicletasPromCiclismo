from datetime import date

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.auth import require_admin, require_authentication
from app.extensions import db
from app.models import Event

events_bp = Blueprint("events", __name__, url_prefix="/events")

REQUIRED_FIELDS = {"name", "date", "location", "description"}


def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("'date' must be a valid ISO date (YYYY-MM-DD)") from exc


def _validate_payload(payload: dict) -> dict:
    missing_fields = sorted(field for field in REQUIRED_FIELDS if not payload.get(field))
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"Missing required fields: {missing}")

    return {
        "name": payload["name"].strip(),
        "date": _parse_iso_date(payload["date"]),
        "location": payload["location"].strip(),
        "description": payload["description"].strip(),
    }


@events_bp.post("/events")
@require_admin
def create_event():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    event = Event(**validated_payload)

    try:
        db.session.add(event)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not save event"}), 500

    return jsonify(event.to_dict()), 201


@events_bp.put("/events/<int:event_id>")
@require_admin
def update_event(event_id: int):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a valid JSON object"}), 400

    event = db.session.get(Event, event_id)
    if event is None:
        abort(404, description="Event not found")

    try:
        validated_payload = _validate_payload(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    for field_name, field_value in validated_payload.items():
        setattr(event, field_name, field_value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not update event"}), 500

    return jsonify(event.to_dict()), 200


@events_bp.delete("/events/<int:event_id>")
@require_admin
def delete_event(event_id: int):
    event = db.session.get(Event, event_id)
    if event is None:
        abort(404, description="Event not found")

    try:
        db.session.delete(event)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Could not delete event"}), 500

    return jsonify({"message": "Event deleted successfully"}), 200


@events_bp.get("/events")
@require_authentication
def list_events():
    events = Event.query.order_by(Event.date.asc()).all()
    return jsonify([event.to_dict() for event in events]), 200

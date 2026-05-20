from types import SimpleNamespace

from flask import Blueprint, abort, current_app, jsonify, request
from pydantic import ValidationError

from app.auth import require_admin, require_authentication
from app.repositories.bike_repository import BikeRepository
from app.schemas.bike import BikeCreate, BikeUpdate
from app.services.bike_service import BikeService

commands_bp = Blueprint("commands_bikes", __name__)


def _get_service() -> BikeService:
    return BikeService(BikeRepository())


@commands_bp.route("/api/v1/bikes", methods=["POST"])
@require_admin
def create_bike():
    try:
        data = BikeCreate.model_validate(request.get_json())
    except ValidationError as e:
        errors = e.errors()
        first = errors[0] if errors else {}
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Invalid value for field '{first.get('loc', ['unknown'])[0]}'.",
            "details": {"errors": [{
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
            } for err in errors]},
        }), 422

    service = _get_service()
    response = service.create_bike(data)

    rabbitmq = current_app.rabbitmq
    if rabbitmq is not None:
        from app.services.rabbitmq_service import (
            BrokerReplyRejectedError,
            BrokerReplyTimeoutError,
            BrokerUnavailableError,
        )

        pub = SimpleNamespace(
            brand=data.brand,
            type=data.type,
            colour=data.colour,
            state=data.state,
            latitude=data.latitude,
            longitude=data.longitude,
            bike_id=response.id,
        )
        try:
            rabbitmq.publish_bike_created(pub)
        except BrokerUnavailableError:
            abort(503, description="Broker unavailable.")
        except BrokerReplyTimeoutError:
            abort(504, description="Broker reply timeout.")
        except BrokerReplyRejectedError:
            abort(502, description="Broker reply rejected.")

    return jsonify(response.model_dump(mode="json")), 201


@commands_bp.route("/api/v1/bikes/<string:id>", methods=["PUT"])
@require_admin
def update_bike(id):
    try:
        data = BikeUpdate.model_validate(request.get_json())
    except ValidationError as e:
        errors = e.errors()
        first = errors[0] if errors else {}
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Invalid value for field '{first.get('loc', ['unknown'])[0]}'.",
            "details": {"errors": [{
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
            } for err in errors]},
        }), 422

    service = _get_service()
    response = service.update_bike(id, data)

    rabbitmq = current_app.rabbitmq
    if rabbitmq is not None and data.state is not None:
        from app.services.rabbitmq_service import BrokerUnavailableError

        try:
            rabbitmq.publish_bike_status_updated(response.id, response.state)
        except BrokerUnavailableError:
            abort(503, description="Broker unavailable.")

    return jsonify(response.model_dump(mode="json")), 200


@commands_bp.route("/api/v1/bikes/<string:id>", methods=["DELETE"])
@require_admin
def delete_bike(id):
    rabbitmq = current_app.rabbitmq
    if rabbitmq is not None:
        from app.services.rabbitmq_service import (
            BrokerReplyRejectedError,
            BrokerReplyTimeoutError,
            BrokerUnavailableError,
        )

        try:
            rabbitmq.publish_bike_deleted(id)
        except BrokerUnavailableError:
            abort(503, description="Broker unavailable.")
        except BrokerReplyTimeoutError:
            abort(504, description="Broker reply timeout.")
        except BrokerReplyRejectedError:
            abort(502, description="Broker reply rejected.")

    service = _get_service()
    service.delete_bike(id)
    return "", 204

"""Handler for ``bike.created`` (US22) — persist location + RPC reply."""

import logging
from typing import Any

from flask import Flask
from pika.spec import BasicProperties

from app.messaging.rpc import send_rpc_reply
from app.repositories.location_repository import LocationRepository

logger = logging.getLogger(__name__)


def _validate_coords(lat: Any, lng: Any) -> tuple[float, float] | None:
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lng_f <= 180.0):
        return None
    return lat_f, lng_f


def handle_bike_created(
    app: Flask,
    payload: dict,
    channel: Any,
    method: Any,
    properties: BasicProperties,
) -> None:
    """Parse payload, persist ``locations`` row if absent, reply RPC per docs/api-map.md."""
    try:
        bike_id = payload.get("bike_id")
        lat = payload.get("latitude")
        lng = payload.get("longitude")

        if not bike_id or not isinstance(bike_id, str) or not bike_id.strip():
            logger.error("bike.created: missing or invalid bike_id")
            send_rpc_reply(
                channel,
                properties,
                {"status": "error", "message": "missing or invalid bike_id"},
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        coords = _validate_coords(lat, lng)
        if coords is None:
            logger.error("bike.created: missing or invalid latitude/longitude payload=%s", payload)
            send_rpc_reply(
                channel,
                properties,
                {"status": "error", "message": "missing or invalid latitude/longitude"},
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        lat_f, lng_f = coords

        with app.app_context():
            try:
                repo = LocationRepository()
                repo.create_if_absent(bike_id.strip(), lat_f, lng_f)
            except Exception:
                logger.exception("bike.created: persistence failed bike_id=%s", bike_id)
                send_rpc_reply(
                    channel,
                    properties,
                    {"status": "error", "message": "database error"},
                )
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

        send_rpc_reply(channel, properties, {"status": "ok"})
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("bike.created: unexpected error")
        try:
            send_rpc_reply(
                channel,
                properties,
                {"status": "error", "message": "internal error"},
            )
        except Exception:
            logger.exception("bike.created: failed to send RPC error reply")
        try:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass

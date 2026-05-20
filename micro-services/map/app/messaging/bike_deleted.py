import logging
from typing import Any

from flask import Flask
from pika.spec import BasicProperties

from app.messaging.rpc import send_rpc_reply
from app.repositories.location_repository import LocationRepository

logger = logging.getLogger(__name__)


def handle_bike_deleted(
    app: Flask,
    payload: dict,
    channel: Any,
    method: Any,
    properties: BasicProperties,
) -> None:
    try:
        bike_id = payload.get("bike_id") or payload.get("bikeId")
        if not bike_id or not isinstance(bike_id, str) or not bike_id.strip():
            logger.error("bike.deleted: missing or invalid bike_id payload=%s", payload)
            send_rpc_reply(
                channel,
                properties,
                {"status": "error", "message": "missing or invalid bike_id"},
            )
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        with app.app_context():
            repo = LocationRepository()
            repo.delete_by_bike_id(bike_id.strip())  # idempotent

        send_rpc_reply(channel, properties, {"status": "ok"})
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("bike.deleted: unexpected error")
        try:
            send_rpc_reply(
                channel,
                properties,
                {"status": "error", "message": "internal error"},
            )
        except Exception:
            logger.exception("bike.deleted: failed to send RPC error reply")
        try:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass


"""Handler for ``bike.statusUpdated`` (US23) — update location status only, no RPC."""

import logging
from typing import Any

from flask import Flask
from pika.spec import BasicProperties

from app.models.location import LocationStatus
from app.repositories.location_repository import LocationRepository

logger = logging.getLogger(__name__)


def _parse_map_status(raw: Any) -> LocationStatus | None:
    if raw is None or not isinstance(raw, str):
        return None
    normalized = raw.strip().lower()
    if normalized == "available":
        return LocationStatus.available
    if normalized == "unavailable":
        return LocationStatus.unavailable
    return None


def handle_bike_status_updated(
    app: Flask,
    payload: dict,
    channel: Any,
    method: Any,
    properties: BasicProperties,
) -> None:
    """Parse payload, update ``locations.status`` if row exists; ack always (no RPC)."""
    try:
        bike_id = payload.get("bikeId") or payload.get("bike_id")
        if not bike_id or not isinstance(bike_id, str) or not bike_id.strip():
            logger.error("bike.statusUpdated: missing or invalid bikeId / bike_id payload=%s", payload)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        status = _parse_map_status(payload.get("status"))
        if status is None:
            logger.error("bike.statusUpdated: invalid or missing status payload=%s", payload)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        with app.app_context():
            try:
                repo = LocationRepository()
                updated = repo.update_status(bike_id.strip(), status)
            except Exception:
                logger.exception("bike.statusUpdated: persistence failed bike_id=%s", bike_id)
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            if not updated:
                logger.warning(
                    "bike.statusUpdated: no location row for bike_id=%s (no update)",
                    bike_id.strip(),
                )

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("bike.statusUpdated: unexpected error")
        try:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass

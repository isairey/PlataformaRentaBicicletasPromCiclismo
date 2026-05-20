"""Background RabbitMQ consumers."""

import logging
import threading
from typing import Any

import pika
from flask import Flask

from app.messaging.rpc import send_rpc_reply

logger = logging.getLogger(__name__)


def _stub_rpc_ok(
    _app: Flask,
    _payload: dict,
    channel: pika.channel.Channel,
    method: Any,
    properties: pika.spec.BasicProperties,
) -> None:
    """Other queues still use Bike CRUD RPC — reply ok so the publisher does not timeout."""
    if properties.reply_to:
        send_rpc_reply(channel, properties, {"status": "ok"})
    channel.basic_ack(delivery_tag=method.delivery_tag)


def register_consumers(app: Flask) -> None:
    if app.config.get("TESTING"):
        return
    if not app.config.get("ENABLE_RABBIT_CONSUMERS"):
        logger.info("RabbitMQ consumers off (set ENABLE_RABBIT_CONSUMERS=1 when broker is up).")
        return

    try:
        from app.messaging.bike_created import handle_bike_created
        from app.messaging.bike_deleted import handle_bike_deleted
        from app.messaging.bike_status_updated import handle_bike_status_updated
        from app.messaging.consumer import consume_forever

        created_key = app.config["RABBITMQ_ROUTING_KEY_BIKE_CREATED"]
        status_key = app.config["RABBITMQ_ROUTING_KEY_BIKE_STATUS_UPDATED"]
        deleted_key = app.config["RABBITMQ_ROUTING_KEY_BIKE_DELETED"]

        def _run_bike_created() -> None:
            consume_forever(
                app,
                created_key,
                handle_bike_created,
            )

        t1 = threading.Thread(
            target=_run_bike_created,
            daemon=True,
            name=f"amqp-{created_key}",
        )
        t1.start()
        logger.info("Started consumer thread for routing_key=%s", created_key)

        def _run_bike_status_updated() -> None:
            consume_forever(app, status_key, handle_bike_status_updated)

        t_status = threading.Thread(
            target=_run_bike_status_updated,
            daemon=True,
            name=f"amqp-{status_key}",
        )
        t_status.start()
        logger.info("Started consumer thread for routing_key=%s", status_key)

        t_deleted = threading.Thread(
            target=lambda: consume_forever(app, deleted_key, handle_bike_deleted),
            daemon=True,
            name=f"amqp-{deleted_key}",
        )
        t_deleted.start()
        logger.info("Started consumer thread for routing_key=%s", deleted_key)

    except Exception:
        logger.exception("Could not start RabbitMQ consumers (broker up?)")

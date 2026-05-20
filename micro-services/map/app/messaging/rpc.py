"""RPC reply helper for RabbitMQ request–reply (docs/api-map.md)."""

import json
import logging
from typing import Any

import pika

logger = logging.getLogger(__name__)


def send_rpc_reply(
    channel: pika.channel.Channel,
    properties: pika.spec.BasicProperties,
    body: dict[str, Any],
) -> None:
    """Publish JSON to the reply queue named in ``properties.reply_to``."""
    if not properties.reply_to:
        logger.warning("RPC reply skipped: missing reply_to on incoming message")
        return
    corr = properties.correlation_id
    channel.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        body=json.dumps(body).encode("utf-8"),
        properties=pika.BasicProperties(correlation_id=corr),
    )

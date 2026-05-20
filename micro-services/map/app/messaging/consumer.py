"""RabbitMQ consumer wiring for map service.

``bike.created`` uses request–reply (RPC): see ``docs/api-map.md``.
"""

import json
import logging
from typing import Any, Callable

import pika
from flask import Flask

from app.messaging.rpc import send_rpc_reply

logger = logging.getLogger(__name__)

# (app, payload, channel, method, properties) -> None;
MessageHandler = Callable[[Flask, dict, Any, Any, pika.spec.BasicProperties], None]


def declare_binding(channel: pika.channel.Channel, exchange: str, routing_key: str) -> None:
    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=routing_key, durable=True)
    channel.queue_bind(queue=routing_key, exchange=exchange, routing_key=routing_key)


def consume_forever(
    app: Flask,
    routing_key: str,
    handler: MessageHandler,
) -> None:
    url = app.config["RABBITMQ_URL"]
    exchange = app.config["RABBITMQ_EXCHANGE"]

    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    declare_binding(channel, exchange, routing_key)

    def _callback(
        ch: pika.channel.Channel,
        method: Any,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Invalid JSON on %s: %s", routing_key, e)
            # Solo responder por RPC si el publicador espera reply (p. ej. bike.created).
            if properties.reply_to:
                send_rpc_reply(
                    ch,
                    properties,
                    {"status": "error", "message": "invalid json body"},
                )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        try:
            handler(app, payload, ch, method, properties)
        except Exception:
            logger.exception("Handler failed for routing_key=%s", routing_key)
            if properties.reply_to:
                try:
                    send_rpc_reply(
                        ch,
                        properties,
                        {"status": "error", "message": "handler error"},
                    )
                except Exception:
                    logger.exception("Failed to send RPC error reply")
            try:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                pass

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=routing_key, on_message_callback=_callback, auto_ack=False)
    logger.info("Consuming queue=%s exchange=%s", routing_key, exchange)
    channel.start_consuming()

import pika
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)


def _publish(routing_key: str, payload: dict):
    url         = current_app.config["RABBITMQ_URL"]
    exchange    = current_app.config["RABBITMQ_EXCHANGE"]

    params     = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel    = connection.channel()

    channel.exchange_declare(
        exchange=exchange,
        exchange_type="direct",
        durable=True
    )

    channel.queue_declare(queue=routing_key, durable=True)
    channel.queue_bind(
        queue=routing_key,
        exchange=exchange,
        routing_key=routing_key
    )

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json"
        )
    )

    connection.close()
    logger.info(f"Evento '{routing_key}' publicado: {payload}")


def publish_rental_started(rental_dict: dict):
    try:
        routing_key = current_app.config["RABBITMQ_ROUTING_KEY"]
        _publish(routing_key, rental_dict)
    except Exception as e:
        logger.error(f"Error publicando rental.started: {e}")
        raise


def publish_rental_ended(rental_dict: dict):
    try:
        _publish("rental.completed", {
            "rentalId": rental_dict["rentalId"],
            "bikeId":   rental_dict["bikeId"],
            "userId":   rental_dict["userId"],
            "endTime":  rental_dict["endTime"],
        })
    except Exception as e:
        logger.error(f"Error publicando rental.completed: {e}")
        raise

import pika
import json
import logging
from uuid import uuid4
from flask import current_app

logger = logging.getLogger(__name__)


def _publish(routing_key: str, payload: dict):
    url      = current_app.config["RABBITMQ_URL"]
    exchange = current_app.config["RABBITMQ_EXCHANGE"]

    params     = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel    = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=routing_key, durable=True)
    channel.queue_bind(queue=routing_key, exchange=exchange, routing_key=routing_key)

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
    )

    connection.close()
    logger.info(f"Evento '{routing_key}' publicado: {payload}")


def publish_rental_started(rental_dict: dict):
    try:
        routing_key = current_app.config["RABBITMQ_ROUTING_KEY"]
        _publish(routing_key, rental_dict)
    except Exception as e:
        logger.error(f"Error publicando rental.started: {e}")
        raise


def publish_rental_ended(rental_dict: dict):
    try:
        _publish("rental.completed", {
            "rentalId": rental_dict["rentalId"],
            "bikeId":   rental_dict["bikeId"],
            "userId":   rental_dict["userId"],
            "endTime":  rental_dict["endTime"],
        })
    except Exception as e:
        logger.error(f"Error publicando rental.completed: {e}")
        raise



_RPC_TIMEOUT = 12


def _rpc_call(queue: str, payload: dict) -> dict:
    """Envía un mensaje RPC y espera la respuesta en una cola exclusiva."""
    url    = current_app.config["RABBITMQ_URL"]
    params = pika.URLParameters(url)

    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()

        # Cola de respuesta anónima, exclusiva y auto-eliminable
        result         = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        callback_queue = result.method.queue

        correlation_id = str(uuid4())
        response       = [None]

        def on_response(ch, method, properties, body):
            if properties.correlation_id == correlation_id:
                response[0] = body

        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=True,
        )

        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=correlation_id,
            ),
        )

        connection.process_data_events(time_limit=_RPC_TIMEOUT)

        if response[0] is None:
            raise TimeoutError(f"Sin respuesta RPC en '{queue}' tras {_RPC_TIMEOUT}s")

        return json.loads(response[0])

    finally:
        if connection.is_open:
            connection.close()


def check_bike_available(bike_id: str) -> bool:

    reply = _rpc_call("rental.isAvailable", {"bike_id": bike_id})
    return reply.get("available", False)
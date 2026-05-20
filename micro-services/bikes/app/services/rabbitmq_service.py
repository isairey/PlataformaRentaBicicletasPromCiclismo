import json
import logging
import threading
from datetime import datetime, timezone
from uuid import uuid4

import pika
import pika.exceptions

from app.models.bike import BikeState

logger = logging.getLogger(__name__)


def bike_state_to_map_location_status(state: BikeState) -> str:
    if state == BikeState.Free:
        return "available"
    if state == BikeState.Rented:
        return "unavailable"
    raise ValueError(f"Unsupported BikeState for map sync: {state!r}")


class BrokerUnavailableError(Exception):
    pass


class BrokerReplyTimeoutError(Exception):
    pass


class BrokerReplyRejectedError(Exception):
    pass


class RabbitMQService:
    QUEUES = [
        "bike.created",
        "bike.statusUpdated",
        "bike.deleted",
        "rental.started",
        "rental.completed",
        "rental.isAvailable",
    ]

    def __init__(self, app=None):
        self._app = None
        self._url = None
        self._reply_timeout = 10
        self._enabled = False
        self._stopped = False
        self._consumer_thread = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        self._url = app.config.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self._reply_timeout = app.config.get("RABBITMQ_REPLY_TIMEOUT", 10)
        self._enabled = app.config.get("RABBITMQ_ENABLED", True)

        if self._enabled:
            self._start()

    def _start(self):
        try:
            connection = self._connect()
            channel = connection.channel()
            self._declare_queues(channel)
            connection.close()
            logger.info("[RABBITMQ] Connected and declared queues")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error("[RABBITMQ] ERROR model=startup queue=None bike_id=None correlation_id=None error=AMQPConnectionError: %s", e)
            return

        self._start_consumer_thread()

    def _connect(self):
        params = pika.URLParameters(self._url)
        return pika.BlockingConnection(params)

    def _declare_queues(self, channel):
        for queue in self.QUEUES:
            channel.queue_declare(queue=queue, durable=True)

    def _rpc_call(self, queue, payload):
        if not self._enabled:
            raise BrokerUnavailableError("Broker is disabled")

        connection = None
        try:
            connection = self._connect()
        except pika.exceptions.AMQPConnectionError as e:
            raise BrokerUnavailableError(str(e)) from e

        try:
            channel = connection.channel()

            result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
            callback_queue = result.method.queue

            correlation_id = str(uuid4())
            response = [None]

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

            connection.process_data_events(time_limit=self._reply_timeout)

            if response[0] is None:
                raise BrokerReplyTimeoutError(
                    f"No reply received within {self._reply_timeout}s for queue '{queue}'"
                )

            try:
                reply = json.loads(response[0])
            except (json.JSONDecodeError, TypeError):
                raise BrokerReplyRejectedError("Invalid JSON in reply")

            if reply.get("status", "").lower() != "ok":
                raise BrokerReplyRejectedError(
                    f"Reply status is '{reply.get('status')}', expected 'ok'"
                )

        except (BrokerReplyTimeoutError, BrokerReplyRejectedError):
            raise
        except pika.exceptions.AMQPConnectionError as e:
            raise BrokerUnavailableError(str(e)) from e
        finally:
            if connection and connection.is_open:
                connection.close()

    def _publish_fire_and_forget(self, queue_name: str, payload: dict) -> None:
        """Publish to the default exchange; no RPC / no reply expected."""
        if not self._enabled:
            raise BrokerUnavailableError("Broker is disabled")

        connection = None
        try:
            connection = self._connect()
        except pika.exceptions.AMQPConnectionError as e:
            raise BrokerUnavailableError(str(e)) from e

        try:
            channel = connection.channel()
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )
        except pika.exceptions.AMQPConnectionError as e:
            raise BrokerUnavailableError(str(e)) from e
        finally:
            if connection and connection.is_open:
                connection.close()

    def publish_bike_created(self, bike_data):
        if not self._enabled:
            raise BrokerUnavailableError("Broker is disabled")

        bike_id = getattr(bike_data, "bike_id", None) or str(uuid4())
        payload = {
            "event_type": "bike.created",
            "bike_id": bike_id,
            "latitude": getattr(bike_data, "latitude", None),
            "longitude": getattr(bike_data, "longitude", None),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "brand": bike_data.brand,
                "type": bike_data.type.value if hasattr(bike_data.type, "value") else str(bike_data.type),
                "colour": bike_data.colour,
                "state": bike_data.state.value if hasattr(bike_data.state, "value") else str(bike_data.state),
            },
        }
        self._rpc_call("bike.created", payload)

    def publish_bike_deleted(self, bike_id):
        if not self._enabled:
            raise BrokerUnavailableError("Broker is disabled")

        payload = {
            "event_type": "bike.deleted",
            "bike_id": str(bike_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {},
        }
        self._rpc_call("bike.deleted", payload)

    def publish_bike_status_updated(self, bike_id: str, bike_state: BikeState) -> None:
        """US23: notify Map of availability change (one-way, no RPC)."""
        if not self._enabled:
            raise BrokerUnavailableError("Broker is disabled")

        map_status = bike_state_to_map_location_status(bike_state)
        payload = {
            "event_type": "bike.statusUpdated",
            "bikeId": str(bike_id),
            "status": map_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._publish_fire_and_forget("bike.statusUpdated", payload)

    def _start_consumer_thread(self):
        self._stopped = False
        self._consumer_thread = threading.Thread(
            target=self._consume_loop, daemon=True
        )
        self._consumer_thread.start()
        logger.info("[RABBITMQ] Consumer thread started")

    def _consume_loop(self):
        import time

        while not self._stopped:
            try:
                connection = self._connect()
                channel = connection.channel()
                self._declare_queues(channel)
                self._consume(channel)
            except pika.exceptions.AMQPError as e:
                logger.error(
                    "[RABBITMQ] ERROR model=async queue=consumer bike_id=None "
                    "correlation_id=None error=%s: %s",
                    type(e).__name__,
                    e,
                )
                if not self._stopped:
                    time.sleep(5)
            except Exception as e:
                logger.error(
                    "[RABBITMQ] ERROR model=async queue=consumer bike_id=None "
                    "correlation_id=None error=%s: %s",
                    type(e).__name__,
                    e,
                )
                if not self._stopped:
                    time.sleep(5)

    def _consume(self, channel):
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue="rental.started",
            on_message_callback=self._on_rental_started,
            auto_ack=False,
        )
        channel.basic_consume(
            queue="rental.completed",
            on_message_callback=self._on_rental_completed,
            auto_ack=False,
        )
        channel.basic_consume(
            queue="rental.isAvailable",
            on_message_callback=self._on_is_available,
            auto_ack=False,
        )
        channel.start_consuming()

    def _on_rental_started(self, ch, method, properties, body):
        from app.models.bike import BikeState
        logger.info(f"[RABBITMQ] INFO Consuming rental.started event model=async queue={method.routing_key} body={body}")
        
        self._handle_rental_event(ch, method, body, target_state=BikeState.Rented)

    def _on_rental_completed(self, ch, method, properties, body):
        from app.models.bike import BikeState
        logger.info(f"[RABBITMQ] INFO Consuming rental.completed event model=async queue={method.routing_key} body={body}")
        
        self._handle_rental_event(ch, method, body, target_state=BikeState.Free)

    def _handle_rental_event(self, ch, method, body, target_state):
        from uuid import UUID

        from app.repositories.bike_repository import BikeRepository
        from app.services.bike_service import BikeService

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            logger.error(
                "[RABBITMQ] ERROR model=async queue=%s bike_id=None "
                "correlation_id=None error=JSONDecodeError: Malformed message body",
                method.routing_key,
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        bike_id = data.get("bikeId")

        logger.info(f"[RABBITMQ] INFO model=async queue={method.routing_key} bikeId={bike_id}")
        
        if not bike_id:
            logger.error(
                "[RABBITMQ] ERROR model=async queue=%s bike_id=None "
                "correlation_id=None error=ValueError: Missing bike_id field",
                method.routing_key,
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            UUID(bike_id)
        except (ValueError, AttributeError):
            logger.error(
                "[RABBITMQ] ERROR model=async queue=%s bike_id=%s "
                "correlation_id=None error=ValueError: Invalid UUID for bike_id",
                method.routing_key,
                bike_id,
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            with self._app.app_context():
                service = BikeService(BikeRepository())
                try:
                    bike_response = service.get_bike(bike_id)
                    logger.info(f"[RABBITMQ] INFO model=async queue={method.routing_key} bikeId={bike_id} bike_response={bike_response}")
                except Exception:
                    logger.warning(
                        "[RABBITMQ] WARNING model=async queue=%s bike_id=%s "
                        "correlation_id=None error=NotFound: Bike not found",
                        method.routing_key,
                        bike_id,
                    )
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return

                if bike_response.state == target_state:
                    logger.info(f"[RABBITMQ] INFO model=async queue={method.routing_key} bikeId={bike_id} bike_response={bike_response} target_state={target_state}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    self.publish_bike_status_updated(bike_id, target_state)
                    
                    return

                from app.schemas.bike import BikeUpdate

                update_data = BikeUpdate(state=target_state)
                service.update_bike(bike_id, update_data)
                logger.info(f"[RABBITMQ] INFO model=async queue={method.routing_key} bikeId={bike_id} update_data={update_data}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(
                    "[RABBITMQ] INFO model=async queue=%s bike_id=%s "
                    "correlation_id=None: State updated to %s",
                    method.routing_key,
                    bike_id,
                    target_state.value,
                )
                self.publish_bike_status_updated(bike_id, target_state)
                logger.info(f"[RABBITMQ] INFO model=async queue={method.routing_key} bikeId={bike_id} published bike_status_updated")
        except Exception as e:
            logger.error(
                "[RABBITMQ] ERROR model=async queue=%s bike_id=%s "
                "correlation_id=None error=%s: %s",
                method.routing_key,
                bike_id,
                type(e).__name__,
                e,
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _on_is_available(self, ch, method, properties, body):
        import time
        import uuid as _uuid

        from app.repositories.bike_repository import BikeRepository

        start = time.monotonic()
        bike_id = None
        correlation_id = getattr(properties, "correlation_id", None)
        reply_to = getattr(properties, "reply_to", None)

        def _publish_reply(payload):
            ch.basic_publish(
                exchange="",
                routing_key=reply_to,
                body=json.dumps(payload),
                properties=pika.BasicProperties(correlation_id=correlation_id),
            )

        # Guard: no reply_to — cannot reply, discard silently
        if not reply_to:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            logger.info(
                "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=None "
                "correlation_id=%s available=None elapsed_ms=%.1f",
                correlation_id,
                (time.monotonic() - start) * 1000,
            )
            return

        try:
            try:
                data = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                _publish_reply({"available": False, "reason": "error", "message": "Malformed JSON body"})
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                logger.info(
                    "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=None "
                    "correlation_id=%s available=False elapsed_ms=%.1f",
                    correlation_id,
                    (time.monotonic() - start) * 1000,
                )
                return

            bike_id = data.get("bike_id")
            if not bike_id:
                _publish_reply({"available": False, "reason": "error", "message": "Missing bike_id field"})
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                logger.info(
                    "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=None "
                    "correlation_id=%s available=False elapsed_ms=%.1f",
                    correlation_id,
                    (time.monotonic() - start) * 1000,
                )
                return

            try:
                _uuid.UUID(bike_id, version=4)
            except (ValueError, AttributeError):
                _publish_reply({"available": False, "reason": "error", "message": "Invalid bike_id format"})
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                logger.info(
                    "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=%s "
                    "correlation_id=%s available=False elapsed_ms=%.1f",
                    bike_id,
                    correlation_id,
                    (time.monotonic() - start) * 1000,
                )
                return

            with self._app.app_context():
                bike = BikeRepository().get_by_id(bike_id)

            if bike is None:
                _publish_reply({"available": False, "reason": "not_found"})
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(
                    "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=%s "
                    "correlation_id=%s available=False elapsed_ms=%.1f",
                    bike_id,
                    correlation_id,
                    (time.monotonic() - start) * 1000,
                )
                return

            available = bike.state == BikeState.Free
            _publish_reply({"available": available})
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(
                "[RABBITMQ] INFO model=async queue=rental.isAvailable bike_id=%s "
                "correlation_id=%s available=%s elapsed_ms=%.1f",
                bike_id,
                correlation_id,
                available,
                (time.monotonic() - start) * 1000,
            )

        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error(
                "[RABBITMQ] ERROR model=async queue=rental.isAvailable bike_id=%s "
                "correlation_id=%s error=%s: %s elapsed_ms=%.1f",
                bike_id,
                correlation_id,
                type(e).__name__,
                e,
                elapsed_ms,
            )
            if reply_to:
                try:
                    _publish_reply({"available": False, "reason": "error", "message": str(e)})
                except Exception:
                    pass
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def shutdown(self):
        self._stopped = True
        logger.info("[RABBITMQ] Shutdown requested")

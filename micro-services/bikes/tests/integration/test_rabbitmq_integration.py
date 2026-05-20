import json
import threading
import time

import pika
import pika.exceptions
import pytest

from app.models.bike import BikeState


def _broker_available():
    """Check if RabbitMQ is reachable."""
    try:
        conn = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@localhost:5672/"))
        conn.close()
        return True
    except Exception:
        return False


broker_available = pytest.mark.skipif(
    not _broker_available(),
    reason="RabbitMQ broker not available on localhost:5672",
)


@pytest.mark.integration_broker
@broker_available
class TestRpcBikeCreation:
    """T022: Broker-gated RPC test for bike creation."""

    def test_create_bike_with_rpc_reply(self, app, client):
        """Start a consumer that auto-replies ok on bike.created, then POST a bike."""
        stop_event = threading.Event()
        consumer_started = threading.Event()

        def consumer_thread():
            connection = pika.BlockingConnection(
                pika.URLParameters("amqp://guest:guest@localhost:5672/")
            )
            channel = connection.channel()
            channel.queue_declare(queue="bike.created", durable=True)
            consumer_started.set()

            def on_message(ch, method, properties, body):
                # Reply with {"status": "ok"}
                ch.basic_publish(
                    exchange="",
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id,
                    ),
                    body=json.dumps({"status": "ok"}),
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                stop_event.set()

            channel.basic_consume(
                queue="bike.created",
                on_message_callback=on_message,
                auto_ack=False,
            )

            while not stop_event.is_set():
                connection.process_data_events(time_limit=1)

            connection.close()

        # Enable RabbitMQ for this test
        app.config["RABBITMQ_ENABLED"] = True

        from app.services.rabbitmq_service import RabbitMQService

        rabbitmq = RabbitMQService()
        rabbitmq.init_app(app)
        app.rabbitmq = rabbitmq

        t = threading.Thread(target=consumer_thread, daemon=True)
        t.start()
        consumer_started.wait(timeout=5)

        response = client.post(
            "/api/v1/bikes",
            json={"brand": "Trek", "type": "Mountain", "colour": "Red"},
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["brand"] == "Trek"
        assert data["state"] == "Free"

        stop_event.set()
        t.join(timeout=5)

        # Restore disabled state
        app.config["RABBITMQ_ENABLED"] = False
        app.rabbitmq = None


@pytest.mark.integration_broker
@broker_available
class TestAsyncConsumerRentalStarted:
    """T023: Broker-gated async consumer test for rental.started."""

    def test_rental_started_updates_bike_state(self, app, client):
        """Publish rental.started message, verify bike state becomes Rented."""
        from app import db
        from app.models.bike import Bike, BikeType

        with app.app_context():
            bike = Bike(
                id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                brand="Giant",
                type=BikeType.Street,
                colour="Blue",
                state=BikeState.Free,
            )
            db.session.add(bike)
            db.session.commit()

        # Enable RabbitMQ and start consumer
        app.config["RABBITMQ_ENABLED"] = True

        from app.services.rabbitmq_service import RabbitMQService

        rabbitmq = RabbitMQService()
        rabbitmq.init_app(app)
        app.rabbitmq = rabbitmq
        rabbitmq._start_consumer_thread()

        # Publish rental.started
        connection = pika.BlockingConnection(
            pika.URLParameters("amqp://guest:guest@localhost:5672/")
        )
        channel = connection.channel()
        channel.queue_declare(queue="rental.started", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="rental.started",
            body=json.dumps({
                "event_type": "rental.started",
                "bike_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                "timestamp": "2026-03-24T10:10:00Z",
                "data": {"rental_id": "11111111-2222-3333-4444-555555555555"},
            }),
        )
        connection.close()

        # Wait for consumer to process
        time.sleep(3)

        response = client.get("/api/v1/bikes/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        assert response.status_code == 200
        data = response.get_json()
        assert data["state"] == "Rented"

        # Cleanup
        rabbitmq.shutdown()
        app.config["RABBITMQ_ENABLED"] = False
        app.rabbitmq = None


@pytest.mark.integration_broker
@broker_available
class TestIsAvailableRpc:
    """T009: End-to-end RPC round-trip for rental.isAvailable."""

    def test_is_available_rpc_round_trip(self, app):
        """Seed a Free bike, publish rental.isAvailable RPC, verify reply arrives with available=true."""
        from app import db
        from app.models.bike import Bike, BikeType

        seeded_id = "cccccccc-dddd-4eee-8fff-aaaaaaaaaaaa"

        with app.app_context():
            bike = Bike(
                id=seeded_id,
                brand="Trek",
                type=BikeType.Mountain,
                colour="Red",
                state=BikeState.Free,
            )
            db.session.add(bike)
            db.session.commit()

        # Enable RabbitMQ and start consumer thread
        app.config["RABBITMQ_ENABLED"] = True
        from app.services.rabbitmq_service import RabbitMQService

        rabbitmq = RabbitMQService()
        rabbitmq.init_app(app)
        app.rabbitmq = rabbitmq
        rabbitmq._start_consumer_thread()

        # Give consumer thread time to connect and start consuming
        time.sleep(2)

        # Publish rental.isAvailable RPC
        connection = pika.BlockingConnection(
            pika.URLParameters("amqp://guest:guest@localhost:5672/")
        )
        channel = connection.channel()

        result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        callback_queue = result.method.queue

        reply_received = [None]

        def on_reply(ch, method, props, body):
            reply_received[0] = (props.correlation_id, json.loads(body))

        channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_reply,
            auto_ack=True,
        )

        channel.basic_publish(
            exchange="",
            routing_key="rental.isAvailable",
            body=json.dumps({"bike_id": seeded_id}),
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id="test-corr-1",
            ),
        )

        connection.process_data_events(time_limit=10)
        connection.close()

        assert reply_received[0] is not None, "No reply received within 10s"
        corr_id, body = reply_received[0]
        assert corr_id == "test-corr-1"
        assert body["available"] is True

        # Cleanup
        rabbitmq.shutdown()
        app.config["RABBITMQ_ENABLED"] = False
        app.rabbitmq = None

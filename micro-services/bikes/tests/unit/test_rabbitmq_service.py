import json
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
import pika.exceptions

from app.models.bike import BikeState

from app.services.rabbitmq_service import (
    BrokerReplyRejectedError,
    BrokerReplyTimeoutError,
    BrokerUnavailableError,
    RabbitMQService,
    bike_state_to_map_location_status,
)


@pytest.fixture
def rabbitmq_service(app):
    """Create a RabbitMQService with broker disabled (no real connections)."""
    service = RabbitMQService()
    service._app = app
    service._url = "amqp://guest:guest@localhost:5672/"
    service._reply_timeout = 10
    service._enabled = True
    return service


class TestPublishBikeCreatedSuccess:
    """T011: Unit tests for publish_bike_created success path."""

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_created_success(self, mock_connect, rabbitmq_service):
        """Positive reply with matching correlation_id completes without raising."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        # Simulate queue_declare returning a named reply queue
        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-123"
        mock_channel.queue_declare.return_value = mock_result

        # Capture the on_message_callback and simulate a positive reply
        def fake_basic_consume(queue, on_message_callback, auto_ack):
            # Store callback for later invocation
            mock_channel._on_message_callback = on_message_callback

        mock_channel.basic_consume.side_effect = fake_basic_consume

        def fake_process_data_events(time_limit):
            # Get the correlation_id from the publish call
            publish_call = mock_channel.basic_publish.call_args
            props = publish_call.kwargs.get("properties") or publish_call[1].get("properties")
            corr_id = props.correlation_id

            # Simulate reply with matching correlation_id and status "ok"
            mock_props = MagicMock()
            mock_props.correlation_id = corr_id
            mock_method = MagicMock()
            mock_channel._on_message_callback(
                mock_channel, mock_method, mock_props,
                json.dumps({"status": "ok"}).encode()
            )

        mock_connection.process_data_events.side_effect = fake_process_data_events

        # Create fake bike data
        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")
        bike_data.bike_id = None
        bike_data.latitude = 6.2442
        bike_data.longitude = -75.5812

        # Should complete without raising
        rabbitmq_service.publish_bike_created(bike_data)

        # Verify publish was called with correct queue
        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args.kwargs or dict(
            zip(["exchange", "routing_key", "body", "properties"],
                mock_channel.basic_publish.call_args.args)
        )
        assert call_kwargs.get("routing_key") == "bike.created"

        # Verify body contains required fields
        body = json.loads(call_kwargs.get("body"))
        assert body["event_type"] == "bike.created"
        assert "bike_id" in body
        assert body["latitude"] == 6.2442
        assert body["longitude"] == -75.5812
        assert "timestamp" in body
        assert body["data"]["brand"] == "Trek"
        assert body["data"]["type"] == "Mountain"
        assert body["data"]["colour"] == "Red"
        assert body["data"]["state"] == "Free"

        # Verify AMQP properties
        props = call_kwargs.get("properties")
        assert props.reply_to == "amq.gen-reply-123"
        assert props.correlation_id is not None


class TestPublishBikeCreatedFailures:
    """T012: Unit tests for publish_bike_created failure paths."""

    @patch.object(RabbitMQService, "_connect")
    def test_connection_failure_raises_broker_unavailable(self, mock_connect, rabbitmq_service):
        """AMQPConnectionError raises BrokerUnavailableError."""
        mock_connect.side_effect = pika.exceptions.AMQPConnectionError("Connection refused")

        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")
        bike_data.bike_id = None
        bike_data.latitude = 6.2442
        bike_data.longitude = -75.5812

        with pytest.raises(BrokerUnavailableError):
            rabbitmq_service.publish_bike_created(bike_data)

    @patch.object(RabbitMQService, "_connect")
    def test_timeout_raises_broker_reply_timeout(self, mock_connect, rabbitmq_service):
        """No reply within timeout raises BrokerReplyTimeoutError."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-123"
        mock_channel.queue_declare.return_value = mock_result

        mock_channel.basic_consume.return_value = None
        # process_data_events returns without invoking callback (timeout)
        mock_connection.process_data_events.return_value = None

        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")
        bike_data.bike_id = None
        bike_data.latitude = 6.2442
        bike_data.longitude = -75.5812

        with pytest.raises(BrokerReplyTimeoutError):
            rabbitmq_service.publish_bike_created(bike_data)

    @patch.object(RabbitMQService, "_connect")
    def test_error_status_raises_broker_reply_rejected(self, mock_connect, rabbitmq_service):
        """Reply with status='error' raises BrokerReplyRejectedError."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-123"
        mock_channel.queue_declare.return_value = mock_result

        def fake_basic_consume(queue, on_message_callback, auto_ack):
            mock_channel._on_message_callback = on_message_callback

        mock_channel.basic_consume.side_effect = fake_basic_consume

        def fake_process_data_events(time_limit):
            publish_call = mock_channel.basic_publish.call_args
            props = publish_call.kwargs.get("properties") or publish_call[1].get("properties")
            corr_id = props.correlation_id
            mock_props = MagicMock()
            mock_props.correlation_id = corr_id
            mock_method = MagicMock()
            mock_channel._on_message_callback(
                mock_channel, mock_method, mock_props,
                json.dumps({"status": "error"}).encode()
            )

        mock_connection.process_data_events.side_effect = fake_process_data_events

        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")
        bike_data.bike_id = None
        bike_data.latitude = 6.2442
        bike_data.longitude = -75.5812

        with pytest.raises(BrokerReplyRejectedError):
            rabbitmq_service.publish_bike_created(bike_data)

    @patch.object(RabbitMQService, "_connect")
    def test_wrong_correlation_id_raises_rejected(self, mock_connect, rabbitmq_service):
        """Reply with wrong correlation_id raises BrokerReplyRejectedError."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-123"
        mock_channel.queue_declare.return_value = mock_result

        def fake_basic_consume(queue, on_message_callback, auto_ack):
            mock_channel._on_message_callback = on_message_callback

        mock_channel.basic_consume.side_effect = fake_basic_consume

        def fake_process_data_events(time_limit):
            # Reply with a WRONG correlation_id - callback doesn't set response[0]
            mock_props = MagicMock()
            mock_props.correlation_id = "wrong-id"
            mock_method = MagicMock()
            mock_channel._on_message_callback(
                mock_channel, mock_method, mock_props,
                json.dumps({"status": "ok"}).encode()
            )

        mock_connection.process_data_events.side_effect = fake_process_data_events

        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")
        bike_data.bike_id = None
        bike_data.latitude = 6.2442
        bike_data.longitude = -75.5812

        # Wrong correlation_id means response[0] stays None -> timeout
        with pytest.raises(BrokerReplyTimeoutError):
            rabbitmq_service.publish_bike_created(bike_data)


class TestPublishBikeDeleted:
    """T015: Unit tests for publish_bike_deleted."""

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_deleted_success(self, mock_connect, rabbitmq_service):
        """Positive reply completes without raising."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-456"
        mock_channel.queue_declare.return_value = mock_result

        def fake_basic_consume(queue, on_message_callback, auto_ack):
            mock_channel._on_message_callback = on_message_callback

        mock_channel.basic_consume.side_effect = fake_basic_consume

        def fake_process_data_events(time_limit):
            publish_call = mock_channel.basic_publish.call_args
            props = publish_call.kwargs.get("properties") or publish_call[1].get("properties")
            corr_id = props.correlation_id
            mock_props = MagicMock()
            mock_props.correlation_id = corr_id
            mock_method = MagicMock()
            mock_channel._on_message_callback(
                mock_channel, mock_method, mock_props,
                json.dumps({"status": "ok"}).encode()
            )

        mock_connection.process_data_events.side_effect = fake_process_data_events

        rabbitmq_service.publish_bike_deleted("3fa85f64-5717-4562-b3fc-2c963f66afa6")

        # Verify publish call
        call_kwargs = mock_channel.basic_publish.call_args.kwargs
        assert call_kwargs["routing_key"] == "bike.deleted"
        body = json.loads(call_kwargs["body"])
        assert body["event_type"] == "bike.deleted"
        assert body["bike_id"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert body["data"] == {}

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_deleted_connection_failure(self, mock_connect, rabbitmq_service):
        """Connection failure raises BrokerUnavailableError."""
        mock_connect.side_effect = pika.exceptions.AMQPConnectionError("Connection refused")

        with pytest.raises(BrokerUnavailableError):
            rabbitmq_service.publish_bike_deleted("some-id")

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_deleted_timeout(self, mock_connect, rabbitmq_service):
        """Timeout raises BrokerReplyTimeoutError."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-456"
        mock_channel.queue_declare.return_value = mock_result
        mock_channel.basic_consume.return_value = None
        mock_connection.process_data_events.return_value = None

        with pytest.raises(BrokerReplyTimeoutError):
            rabbitmq_service.publish_bike_deleted("some-id")

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_deleted_rejected(self, mock_connect, rabbitmq_service):
        """Non-positive reply raises BrokerReplyRejectedError."""
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        mock_result = MagicMock()
        mock_result.method.queue = "amq.gen-reply-456"
        mock_channel.queue_declare.return_value = mock_result

        def fake_basic_consume(queue, on_message_callback, auto_ack):
            mock_channel._on_message_callback = on_message_callback

        mock_channel.basic_consume.side_effect = fake_basic_consume

        def fake_process_data_events(time_limit):
            publish_call = mock_channel.basic_publish.call_args
            props = publish_call.kwargs.get("properties") or publish_call[1].get("properties")
            corr_id = props.correlation_id
            mock_props = MagicMock()
            mock_props.correlation_id = corr_id
            mock_method = MagicMock()
            mock_channel._on_message_callback(
                mock_channel, mock_method, mock_props,
                json.dumps({"status": "rejected"}).encode()
            )

        mock_connection.process_data_events.side_effect = fake_process_data_events

        with pytest.raises(BrokerReplyRejectedError):
            rabbitmq_service.publish_bike_deleted("some-id")


class TestBikeStateToMapLocationStatus:
    def test_free_maps_to_available(self):
        assert bike_state_to_map_location_status(BikeState.Free) == "available"

    def test_rented_maps_to_unavailable(self):
        assert bike_state_to_map_location_status(BikeState.Rented) == "unavailable"


class TestPublishBikeStatusUpdated:
    """US23: one-way publish to bike.statusUpdated queue."""

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_status_updated_rented(self, mock_connect, rabbitmq_service):
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        rabbitmq_service.publish_bike_status_updated(
            "3fa85f64-5717-4562-b3fc-2c963f66afa6", BikeState.Rented
        )

        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args.kwargs
        assert call_kwargs["exchange"] == ""
        assert call_kwargs["routing_key"] == "bike.statusUpdated"
        body = json.loads(call_kwargs["body"])
        assert body["event_type"] == "bike.statusUpdated"
        assert body["bikeId"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert body["status"] == "unavailable"
        assert "timestamp" in body
        assert call_kwargs["properties"].reply_to is None

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_status_updated_free(self, mock_connect, rabbitmq_service):
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        type(mock_connection).is_open = PropertyMock(return_value=True)

        rabbitmq_service.publish_bike_status_updated("bid-x", BikeState.Free)

        body = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert body["status"] == "available"

    @patch.object(RabbitMQService, "_connect")
    def test_publish_bike_status_updated_connection_failure(self, mock_connect, rabbitmq_service):
        mock_connect.side_effect = pika.exceptions.AMQPConnectionError("refused")

        with pytest.raises(BrokerUnavailableError):
            rabbitmq_service.publish_bike_status_updated("id", BikeState.Free)


class TestOnRentalStarted:
    """T019: Unit tests for _on_rental_started / _handle_rental_event."""

    def test_valid_message_updates_bike_to_rented(self, rabbitmq_service, app):
        """Valid message + bike in Free state -> state updated to Rented, basic_ack called."""
        from app.models.bike import BikeState

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        method.routing_key = "rental.started"

        body = json.dumps({
            "event_type": "rental.started",
            "bike_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "timestamp": "2026-03-24T10:10:00Z",
            "data": {"rental_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"},
        }).encode()

        with app.app_context():
            from app import db
            from app.models.bike import Bike, BikeType

            bike = Bike(
                id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                brand="Trek",
                type=BikeType.Mountain,
                colour="Red",
                state=BikeState.Free,
            )
            db.session.add(bike)
            db.session.commit()

            rabbitmq_service._on_rental_started(ch, method, None, body)

            db.session.refresh(bike)
            assert bike.state == BikeState.Rented
            ch.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_already_rented_is_idempotent(self, rabbitmq_service, app):
        """Bike already Rented -> no update, basic_ack called."""
        from app.models.bike import BikeState

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 2
        method.routing_key = "rental.started"

        body = json.dumps({
            "event_type": "rental.started",
            "bike_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "timestamp": "2026-03-24T10:10:00Z",
            "data": {},
        }).encode()

        with app.app_context():
            from app import db
            from app.models.bike import Bike, BikeType

            bike = Bike(
                id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                brand="Trek",
                type=BikeType.Mountain,
                colour="Red",
                state=BikeState.Rented,
            )
            db.session.add(bike)
            db.session.commit()

            rabbitmq_service._on_rental_started(ch, method, None, body)
            ch.basic_ack.assert_called_once_with(delivery_tag=2)

    def test_unknown_bike_nacks(self, rabbitmq_service, app):
        """Unknown bike_id -> basic_nack(requeue=False)."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 3
        method.routing_key = "rental.started"

        body = json.dumps({
            "event_type": "rental.started",
            "bike_id": "00000000-0000-0000-0000-000000000000",
            "timestamp": "2026-03-24T10:10:00Z",
            "data": {},
        }).encode()

        with app.app_context():
            rabbitmq_service._on_rental_started(ch, method, None, body)
            ch.basic_nack.assert_called_once_with(delivery_tag=3, requeue=False)

    def test_malformed_json_nacks(self, rabbitmq_service, app):
        """Malformed JSON body -> basic_nack(requeue=False)."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 4
        method.routing_key = "rental.started"

        with app.app_context():
            rabbitmq_service._on_rental_started(ch, method, None, b"not-json")
            ch.basic_nack.assert_called_once_with(delivery_tag=4, requeue=False)

    def test_missing_bike_id_nacks(self, rabbitmq_service, app):
        """Missing bike_id field -> basic_nack(requeue=False)."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 5
        method.routing_key = "rental.started"

        body = json.dumps({"event_type": "rental.started", "timestamp": "2026-03-24T10:10:00Z"}).encode()

        with app.app_context():
            rabbitmq_service._on_rental_started(ch, method, None, body)
            ch.basic_nack.assert_called_once_with(delivery_tag=5, requeue=False)


class TestOnRentalCompleted:
    """T021: Unit tests for _on_rental_completed."""

    def test_valid_message_updates_bike_to_free(self, rabbitmq_service, app):
        """Valid message + bike Rented -> state updated to Free, basic_ack called."""
        from app.models.bike import BikeState

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        method.routing_key = "rental.completed"

        body = json.dumps({
            "event_type": "rental.completed",
            "bike_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "timestamp": "2026-03-24T10:50:00Z",
            "data": {"rental_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"},
        }).encode()

        with app.app_context():
            from app import db
            from app.models.bike import Bike, BikeType

            bike = Bike(
                id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                brand="Trek",
                type=BikeType.Mountain,
                colour="Red",
                state=BikeState.Rented,
            )
            db.session.add(bike)
            db.session.commit()

            rabbitmq_service._on_rental_completed(ch, method, None, body)

            db.session.refresh(bike)
            assert bike.state == BikeState.Free
            ch.basic_ack.assert_called_once_with(delivery_tag=1)

    def test_already_free_is_idempotent(self, rabbitmq_service, app):
        """Bike already Free -> no update, basic_ack called."""
        from app.models.bike import BikeState

        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 2
        method.routing_key = "rental.completed"

        body = json.dumps({
            "event_type": "rental.completed",
            "bike_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "timestamp": "2026-03-24T10:50:00Z",
            "data": {},
        }).encode()

        with app.app_context():
            from app import db
            from app.models.bike import Bike, BikeType

            bike = Bike(
                id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                brand="Trek",
                type=BikeType.Mountain,
                colour="Red",
                state=BikeState.Free,
            )
            db.session.add(bike)
            db.session.commit()

            rabbitmq_service._on_rental_completed(ch, method, None, body)
            ch.basic_ack.assert_called_once_with(delivery_tag=2)

    def test_unknown_bike_nacks(self, rabbitmq_service, app):
        """Unknown bike_id -> basic_nack(requeue=False)."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 3
        method.routing_key = "rental.completed"

        body = json.dumps({
            "event_type": "rental.completed",
            "bike_id": "00000000-0000-0000-0000-000000000000",
            "timestamp": "2026-03-24T10:50:00Z",
            "data": {},
        }).encode()

        with app.app_context():
            rabbitmq_service._on_rental_completed(ch, method, None, body)
            ch.basic_nack.assert_called_once_with(delivery_tag=3, requeue=False)

    def test_malformed_json_nacks(self, rabbitmq_service, app):
        """Malformed JSON body -> basic_nack(requeue=False)."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 4
        method.routing_key = "rental.completed"

        with app.app_context():
            rabbitmq_service._on_rental_completed(ch, method, None, b"{bad-json")
            ch.basic_nack.assert_called_once_with(delivery_tag=4, requeue=False)


class TestOnIsAvailableHappyPath:
    """T005: Unit tests for _on_rental.isAvailable happy path."""

    BIKE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    def _make(self, delivery_tag=1, bike_id=None):
        bike_id = bike_id or self.BIKE_ID
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = delivery_tag
        properties = MagicMock()
        properties.reply_to = "amq.gen-reply-test"
        properties.correlation_id = "corr-test-1"
        body = json.dumps({"bike_id": bike_id}).encode()
        return ch, method, properties, body

    @patch("app.repositories.bike_repository.BikeRepository")
    def test_bike_free_replies_available_true(self, mock_repo_cls, rabbitmq_service):
        """bike exists, state == Free → reply {"available": true}, basic_ack called."""
        ch, method, properties, body = self._make()
        mock_bike = MagicMock()
        mock_bike.state = BikeState.Free
        mock_repo_cls.return_value.get_by_id.return_value = mock_bike

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_ack.assert_called_once_with(delivery_tag=1)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["available"] is True

    @patch("app.repositories.bike_repository.BikeRepository")
    def test_bike_rented_replies_available_false(self, mock_repo_cls, rabbitmq_service):
        """bike exists, state == Rented → reply {"available": false}, basic_ack called."""
        ch, method, properties, body = self._make()
        mock_bike = MagicMock()
        mock_bike.state = BikeState.Rented
        mock_repo_cls.return_value.get_by_id.return_value = mock_bike

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_ack.assert_called_once_with(delivery_tag=1)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["available"] is False


class TestOnIsAvailableErrorPaths:
    """T007: Unit tests for _on_is_available error paths."""

    BIKE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    def _make(self, delivery_tag=1, bike_id=None, reply_to="amq.gen-reply-test"):
        bike_id = bike_id or self.BIKE_ID
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = delivery_tag
        properties = MagicMock()
        properties.reply_to = reply_to
        properties.correlation_id = "corr-err-1"
        body = json.dumps({"bike_id": bike_id}).encode()
        return ch, method, properties, body

    def test_no_reply_to_nacks_without_reply(self, rabbitmq_service):
        """properties.reply_to = None → basic_nack called, basic_publish NOT called."""
        ch, method, properties, body = self._make(reply_to=None)
        properties.reply_to = None

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_nack.assert_called_once_with(delivery_tag=1, requeue=False)
        ch.basic_publish.assert_not_called()

    def test_malformed_json_nacks_and_replies_error(self, rabbitmq_service):
        """body is b'not-json' → basic_nack called, basic_publish called with reason='error'."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        properties.reply_to = "amq.gen-reply-test"
        properties.correlation_id = "corr-err-1"

        rabbitmq_service._on_is_available(ch, method, properties, b"not-json")

        ch.basic_nack.assert_called_once_with(delivery_tag=1, requeue=False)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["reason"] == "error"

    def test_missing_bike_id_nacks_and_replies_error(self, rabbitmq_service):
        """body has no bike_id → basic_nack called, error reply sent."""
        ch = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        properties = MagicMock()
        properties.reply_to = "amq.gen-reply-test"
        properties.correlation_id = "corr-err-1"

        rabbitmq_service._on_is_available(ch, method, properties, json.dumps({}).encode())

        ch.basic_nack.assert_called_once_with(delivery_tag=1, requeue=False)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["reason"] == "error"

    def test_invalid_uuid_nacks_and_replies_error(self, rabbitmq_service):
        """bike_id='not-a-uuid' → basic_nack called, error reply sent."""
        ch, method, properties, _ = self._make(bike_id="not-a-uuid")
        body = json.dumps({"bike_id": "not-a-uuid"}).encode()

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_nack.assert_called_once_with(delivery_tag=1, requeue=False)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["reason"] == "error"

    @patch("app.repositories.bike_repository.BikeRepository")
    def test_bike_not_found_replies_not_found_and_acks(self, mock_repo_cls, rabbitmq_service):
        """BikeRepository.get_by_id returns None → reply {"available": false, "reason": "not_found"}, basic_ack called."""
        ch, method, properties, body = self._make()
        mock_repo_cls.return_value.get_by_id.return_value = None

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_ack.assert_called_once_with(delivery_tag=1)
        ch.basic_publish.assert_called_once()
        reply = json.loads(ch.basic_publish.call_args.kwargs["body"])
        assert reply["available"] is False
        assert reply["reason"] == "not_found"

    @patch("app.repositories.bike_repository.BikeRepository")
    def test_db_exception_nacks(self, mock_repo_cls, rabbitmq_service):
        """BikeRepository.get_by_id raises Exception → basic_nack called."""
        ch, method, properties, body = self._make()
        mock_repo_cls.return_value.get_by_id.side_effect = Exception("DB connection lost")

        rabbitmq_service._on_is_available(ch, method, properties, body)

        ch.basic_nack.assert_called_once_with(delivery_tag=1, requeue=False)


class TestDisabledMode:
    """T024: RABBITMQ_ENABLED=false guard verification."""

    def test_init_app_disabled_no_connections(self, app):
        """When disabled, init_app completes without opening connections."""
        service = RabbitMQService()
        # Override config to disable
        app.config["RABBITMQ_ENABLED"] = False

        with patch.object(RabbitMQService, "_connect") as mock_connect:
            service.init_app(app)
            mock_connect.assert_not_called()

        assert service._enabled is False

    def test_publish_bike_created_disabled_raises(self, app):
        """When disabled, publish_bike_created raises BrokerUnavailableError."""
        service = RabbitMQService()
        service._enabled = False

        bike_data = MagicMock()
        bike_data.brand = "Trek"
        bike_data.type = MagicMock(value="Mountain")
        bike_data.colour = "Red"
        bike_data.state = MagicMock(value="Free")

        with pytest.raises(BrokerUnavailableError):
            service.publish_bike_created(bike_data)

    def test_publish_bike_deleted_disabled_raises(self, app):
        """When disabled, publish_bike_deleted raises BrokerUnavailableError."""
        service = RabbitMQService()
        service._enabled = False

        with pytest.raises(BrokerUnavailableError):
            service.publish_bike_deleted("some-id")

    def test_publish_bike_status_updated_disabled_raises(self, app):
        """When disabled, publish_bike_status_updated raises BrokerUnavailableError."""
        service = RabbitMQService()
        service._enabled = False

        with pytest.raises(BrokerUnavailableError):
            service.publish_bike_status_updated("some-id", BikeState.Free)

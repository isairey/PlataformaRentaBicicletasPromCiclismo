from unittest.mock import MagicMock

from app import db
from app.messaging.bike_deleted import handle_bike_deleted
from app.models.location import BikeLocation, LocationStatus


def _props(reply_to="amq.gen-reply-1", correlation_id="cid-1"):
    p = MagicMock()
    p.reply_to = reply_to
    p.correlation_id = correlation_id
    return p


class TestHandleBikeDeleted:
    def test_deletes_row_and_replies_ok(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        props = _props()

        payload = {"bike_id": "id-100"}
        with app.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="id-100",
                    latitude=6.2,
                    longitude=-75.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        handle_bike_deleted(app, payload, channel, method, props)

        with app.app_context():
            assert db.session.get(BikeLocation, "id-100") is None

        kw = channel.basic_publish.call_args.kwargs
        assert kw["exchange"] == ""
        assert kw["routing_key"] == props.reply_to
        assert kw["body"] is not None
        # body is JSON bytes
        import json

        assert json.loads(kw["body"].decode())["status"] == "ok"
        channel.basic_ack.assert_called_with(delivery_tag=1)

    def test_missing_row_replies_ok(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 2
        props = _props()
        payload = {"bike_id": "missing-id"}

        handle_bike_deleted(app, payload, channel, method, props)

        kw = channel.basic_publish.call_args.kwargs
        import json

        assert json.loads(kw["body"].decode())["status"] == "ok"
        channel.basic_ack.assert_called_with(delivery_tag=2)

    def test_invalid_payload_replies_error(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 3
        props = _props()
        payload = {"bike_id": ""}

        handle_bike_deleted(app, payload, channel, method, props)

        kw = channel.basic_publish.call_args.kwargs
        import json

        assert json.loads(kw["body"].decode())["status"] == "error"
        channel.basic_ack.assert_called_with(delivery_tag=3)


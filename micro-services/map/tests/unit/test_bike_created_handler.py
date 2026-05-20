import json
from unittest.mock import MagicMock

from app import db
from app.messaging.bike_created import handle_bike_created
from app.models.location import BikeLocation, LocationStatus


def _props(reply_to="amq.gen-reply-1", correlation_id="cid-1"):
    p = MagicMock()
    p.reply_to = reply_to
    p.correlation_id = correlation_id
    return p


class TestHandleBikeCreated:
    def test_inserts_row_and_replies_ok(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        props = _props()
        payload = {
            "bike_id": "id-100",
            "latitude": 6.2442,
            "longitude": -75.5812,
        }
        with app.app_context():
            handle_bike_created(app, payload, channel, method, props)
        with app.app_context():
            row = db.session.get(BikeLocation, "id-100")
            assert row is not None
            assert row.latitude == 6.2442
            assert row.longitude == -75.5812
            assert row.status == LocationStatus.available
        kw = channel.basic_publish.call_args.kwargs
        assert json.loads(kw["body"].decode())["status"] == "ok"
        channel.basic_ack.assert_called_with(delivery_tag=1)

    def test_duplicate_bike_id_replies_ok_without_second_row(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 2
        props = _props()
        payload = {
            "bike_id": "id-200",
            "latitude": 6.0,
            "longitude": -75.0,
        }
        with app.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="id-200",
                    latitude=1.0,
                    longitude=2.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        with app.app_context():
            handle_bike_created(app, payload, channel, method, props)

        with app.app_context():
            rows = db.session.scalars(db.select(BikeLocation).where(BikeLocation.bike_id == "id-200")).all()
            assert len(rows) == 1
            assert rows[0].latitude == 1.0
        kw = channel.basic_publish.call_args.kwargs
        assert json.loads(kw["body"].decode())["status"] == "ok"

    def test_missing_coords_replies_error(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 3
        props = _props()
        payload = {"bike_id": "id-300"}
        with app.app_context():
            handle_bike_created(app, payload, channel, method, props)
        with app.app_context():
            assert db.session.get(BikeLocation, "id-300") is None
        publish_kw = channel.basic_publish.call_args.kwargs
        assert json.loads(publish_kw["body"].decode())["status"] == "error"

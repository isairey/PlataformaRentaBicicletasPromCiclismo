import logging
from unittest.mock import MagicMock

from app import db
from app.messaging.bike_status_updated import handle_bike_status_updated
from app.models.location import BikeLocation, LocationStatus


def _props():
    p = MagicMock()
    p.reply_to = None
    p.correlation_id = None
    return p


class TestHandleBikeStatusUpdated:
    def test_updates_status_when_row_exists(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        props = _props()
        with app.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="id-100",
                    latitude=6.0,
                    longitude=-75.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        payload = {"bikeId": "id-100", "status": "unavailable"}
        with app.app_context():
            handle_bike_status_updated(app, payload, channel, method, props)

        with app.app_context():
            row = db.session.get(BikeLocation, "id-100")
            assert row.status == LocationStatus.unavailable
        channel.basic_ack.assert_called_with(delivery_tag=1)

    def test_accepts_bike_id_snake_case(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 2
        props = _props()
        with app.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="id-201",
                    latitude=6.0,
                    longitude=-75.0,
                    status=LocationStatus.unavailable,
                )
            )
            db.session.commit()

        payload = {"bike_id": "id-201", "status": "AVAILABLE"}
        with app.app_context():
            handle_bike_status_updated(app, payload, channel, method, props)

        with app.app_context():
            row = db.session.get(BikeLocation, "id-201")
            assert row.status == LocationStatus.available

    def test_no_row_warns_and_does_not_insert(self, app, caplog):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 3
        props = _props()
        payload = {"bikeId": "missing-id", "status": "available"}
        with caplog.at_level(logging.WARNING):
            with app.app_context():
                handle_bike_status_updated(app, payload, channel, method, props)

        with app.app_context():
            assert db.session.get(BikeLocation, "missing-id") is None
        channel.basic_ack.assert_called_with(delivery_tag=3)
        assert "no location row" in caplog.text

    def test_invalid_status_does_not_change_db(self, app):
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 4
        props = _props()
        with app.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="id-400",
                    latitude=1.0,
                    longitude=2.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        payload = {"bikeId": "id-400", "status": "damaged"}
        with app.app_context():
            handle_bike_status_updated(app, payload, channel, method, props)

        with app.app_context():
            row = db.session.get(BikeLocation, "id-400")
            assert row.status == LocationStatus.available

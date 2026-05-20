from unittest.mock import MagicMock

from app import db
from app.messaging.bike_status_updated import handle_bike_status_updated
from app.messaging.bike_deleted import handle_bike_deleted
from app.models.location import BikeLocation, LocationStatus


class TestHealthAPI:
    def test_health_returns_ok(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestAvailableLocationsAPI:
    def test_empty_database_returns_empty_array(self, client):
        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_only_available_with_bike_id_shape(self, client):
        with client.application.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="BIKE-101",
                    latitude=6.2442,
                    longitude=-75.5812,
                    status=LocationStatus.available,
                )
            )
            db.session.add(
                BikeLocation(
                    bike_id="BIKE-202",
                    latitude=6.25,
                    longitude=-75.58,
                    status=LocationStatus.unavailable,
                )
            )
            db.session.commit()

        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0] == {
            "bikeId": "BIKE-101",
            "latitude": 6.2442,
            "longitude": -75.5812,
        }

    def test_status_updated_handler_hides_bike_from_available_list(self, client):
        with client.application.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="US23-int",
                    latitude=6.0,
                    longitude=-75.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 99
        props = MagicMock()
        props.reply_to = None
        payload = {"bikeId": "US23-int", "status": "unavailable"}

        with client.application.app_context():
            handle_bike_status_updated(
                client.application, payload, channel, method, props
            )

        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        ids = {item["bikeId"] for item in response.get_json()}
        assert "US23-int" not in ids

    def test_bike_deleted_handler_removes_bike_from_available_list(self, client):
        """US delete propagation: bike.deleted -> handler deletes from locations."""
        with client.application.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="US22-del-int",
                    latitude=6.0,
                    longitude=-75.0,
                    status=LocationStatus.available,
                )
            )
            db.session.commit()

        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 123
        props = MagicMock()
        props.reply_to = None
        props.correlation_id = None
        payload = {"bike_id": "US22-del-int"}

        handle_bike_deleted(client.application, payload, channel, method, props)

        response = client.get("/api/v1/locations/available")
        ids = {item["bikeId"] for item in response.get_json()}
        assert "US22-del-int" not in ids

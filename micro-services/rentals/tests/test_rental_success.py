from unittest.mock import patch, MagicMock

VALID_BIKE = {"id": "bike-001", "state": "Free"}

def test_create_rental_success(client):
    with patch("app.services.rental_service.get_bike") as mock_bike, \
         patch("app.services.rental_service.publish_rental_started") as mock_publish:

        mock_bike.return_value = VALID_BIKE
        mock_publish.return_value = None

        response = client.post("/api/v1/rental", json={
            "userId": "user-123",
            "bikeId": "bike-001"
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data["userId"] == "user-123"
        assert data["bikeId"] == "bike-001"
        assert data["status"] == "ACTIVE"
        assert "rentalId" in data
        assert "startTime" in data
        mock_publish.assert_called_once()


def test_create_rental_publishes_correct_event(client):
    with patch("app.services.rental_service.get_bike") as mock_bike, \
         patch("app.services.rental_service.publish_rental_started") as mock_publish:

        mock_bike.return_value = VALID_BIKE
        mock_publish.return_value = None

        client.post("/api/v1/rental", json={
            "userId": "user-123",
            "bikeId": "bike-001"
        })

        event = mock_publish.call_args[0][0]
        assert event["bikeId"] == "bike-001"
        assert event["userId"] == "user-123"
        assert "rentalId" in event
        assert "startTime" in event


def test_create_rental_rollback_if_rabbitmq_fails(client):
    with patch("app.services.rental_service.get_bike") as mock_bike, \
         patch("app.services.rental_service.publish_rental_started") as mock_publish:

        mock_bike.return_value = VALID_BIKE
        mock_publish.side_effect = Exception("RabbitMQ caído")

        response = client.post("/api/v1/rental", json={
            "userId": "user-123",
            "bikeId": "bike-001"
        })

        assert response.status_code == 500
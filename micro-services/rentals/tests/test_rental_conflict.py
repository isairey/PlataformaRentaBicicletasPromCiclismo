from unittest.mock import patch

def test_bike_unavailable_returns_409(client):
    with patch("app.services.rental_service.get_bike") as mock_bike:
        mock_bike.return_value = {"id": "bike-002", "state": "Rented"}

        response = client.post("/api/v1/rental", json={
            "userId": "user-123",
            "bikeId": "bike-002"
        })

        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data


def test_bike_not_found_returns_404(client):
    with patch("app.services.rental_service.get_bike") as mock_bike:
        mock_bike.return_value = None

        response = client.post("/api/v1/rental", json={
            "userId": "user-123",
            "bikeId": "bike-999"
        })

        assert response.status_code == 404


def test_missing_user_id_returns_400(client):
    response = client.post("/api/v1/rental", json={"bikeId": "bike-001"})
    assert response.status_code == 400


def test_missing_bike_id_returns_400(client):
    response = client.post("/api/v1/rental", json={"userId": "user-123"})
    assert response.status_code == 400


def test_empty_body_returns_400(client):
    response = client.post("/api/v1/rental",
        data="not json",
        content_type="application/json"
    )
    assert response.status_code == 400


def test_empty_fields_returns_400(client):
    response = client.post("/api/v1/rental", json={
        "userId": "  ",
        "bikeId": "  "
    })
    assert response.status_code == 400
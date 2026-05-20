def _bike_json(**overrides):
    payload = {
        "brand": "Trek",
        "type": "Mountain",
        "colour": "Red",
        "latitude": 6.2442,
        "longitude": -75.5812,
    }
    payload.update(overrides)
    return payload


class TestCreateBikeAPI:
    def test_create_bike_success(self, client):
        response = client.post("/api/v1/bikes", json=_bike_json())
        assert response.status_code == 201
        data = response.get_json()
        assert data["brand"] == "Trek"
        assert data["type"] == "Mountain"
        assert data["colour"] == "Red"
        assert data["state"] == "Free"
        assert "id" in data

    def test_create_bike_missing_brand_returns_422(self, client):
        response = client.post("/api/v1/bikes", json={
            "type": "Mountain",
            "colour": "Red",
            "latitude": 6.2442,
            "longitude": -75.5812,
        })
        assert response.status_code == 422
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_bike_invalid_type_returns_422(self, client):
        response = client.post("/api/v1/bikes", json={
            "brand": "Trek",
            "type": "BMX",
            "colour": "Red",
            "latitude": 6.2442,
            "longitude": -75.5812,
        })
        assert response.status_code == 422
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"


class TestListBikesAPI:
    def _create_bike(self, client, **overrides):
        return client.post("/api/v1/bikes", json=_bike_json(**overrides))

    def test_list_bikes_empty(self, client):
        response = client.get("/api/v1/bikes")
        assert response.status_code == 200
        data = response.get_json()
        assert data["bikes"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_bikes_no_filters(self, client):
        self._create_bike(client)
        self._create_bike(client, brand="Giant", colour="Blue")
        response = client.get("/api/v1/bikes")
        data = response.get_json()
        assert data["total"] == 2
        assert len(data["bikes"]) == 2

    def test_list_bikes_filter_by_state(self, client):
        self._create_bike(client, state="Free")
        self._create_bike(client, state="Rented")
        response = client.get("/api/v1/bikes?state=Free")
        data = response.get_json()
        assert data["total"] == 1
        assert data["bikes"][0]["state"] == "Free"

    def test_list_bikes_filter_by_type(self, client):
        self._create_bike(client, type="Mountain")
        self._create_bike(client, type="Street")
        response = client.get("/api/v1/bikes?type=Mountain")
        data = response.get_json()
        assert data["total"] == 1
        assert data["bikes"][0]["type"] == "Mountain"

    def test_list_bikes_combined_filters(self, client):
        self._create_bike(client, type="Mountain", state="Free")
        self._create_bike(client, type="Mountain", state="Rented")
        self._create_bike(client, type="Street", state="Free")
        response = client.get("/api/v1/bikes?type=Mountain&state=Free")
        data = response.get_json()
        assert data["total"] == 1


class TestGetBikeAPI:
    def test_get_bike_success(self, client):
        create_resp = client.post("/api/v1/bikes", json=_bike_json())
        bike_id = create_resp.get_json()["id"]
        response = client.get(f"/api/v1/bikes/{bike_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == bike_id
        assert data["brand"] == "Trek"

    def test_get_bike_not_found(self, client):
        response = client.get("/api/v1/bikes/nonexistent-uuid")
        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "BIKE_NOT_FOUND"


class TestUpdateBikeAPI:
    def _create_bike(self, client):
        resp = client.post("/api/v1/bikes", json=_bike_json(state="Free"))
        return resp.get_json()["id"]

    def test_update_state_publishes_bike_status_updated_when_rabbitmq_enabled(self, app, client):
        from unittest.mock import MagicMock

        from app.models.bike import BikeState

        bike_id = self._create_bike(client)
        mock_rmq = MagicMock()
        app.rabbitmq = mock_rmq

        response = client.put(f"/api/v1/bikes/{bike_id}", json={"state": "Rented"})
        assert response.status_code == 200
        mock_rmq.publish_bike_status_updated.assert_called_once_with(bike_id, BikeState.Rented)

    def test_update_partial_colour_does_not_publish_status_event(self, app, client):
        from unittest.mock import MagicMock

        bike_id = self._create_bike(client)
        mock_rmq = MagicMock()
        app.rabbitmq = mock_rmq

        response = client.put(f"/api/v1/bikes/{bike_id}", json={"colour": "Blue"})
        assert response.status_code == 200
        mock_rmq.publish_bike_status_updated.assert_not_called()

    def test_update_state_free_to_rented(self, client):
        bike_id = self._create_bike(client)
        response = client.put(f"/api/v1/bikes/{bike_id}", json={"state": "Rented"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["state"] == "Rented"

    def test_update_partial_colour(self, client):
        bike_id = self._create_bike(client)
        response = client.put(f"/api/v1/bikes/{bike_id}", json={"colour": "Blue"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["colour"] == "Blue"
        assert data["brand"] == "Trek"  # unchanged

    def test_update_invalid_type_returns_422(self, client):
        bike_id = self._create_bike(client)
        response = client.put(f"/api/v1/bikes/{bike_id}", json={"type": "BMX"})
        assert response.status_code == 422
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_update_not_found(self, client):
        response = client.put("/api/v1/bikes/nonexistent-uuid", json={"colour": "Blue"})
        assert response.status_code == 404


class TestDeleteBikeAPI:
    def _create_bike(self, client):
        resp = client.post("/api/v1/bikes", json=_bike_json())
        return resp.get_json()["id"]

    def test_delete_success(self, client):
        bike_id = self._create_bike(client)
        response = client.delete(f"/api/v1/bikes/{bike_id}")
        assert response.status_code == 204
        assert response.data == b""

    def test_deleted_bike_not_in_get(self, client):
        bike_id = self._create_bike(client)
        client.delete(f"/api/v1/bikes/{bike_id}")
        response = client.get(f"/api/v1/bikes/{bike_id}")
        assert response.status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/api/v1/bikes/nonexistent-uuid")
        assert response.status_code == 404


class TestHealthAPI:
    def test_health_returns_ok(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}

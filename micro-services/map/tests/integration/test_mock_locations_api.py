"""Pruebas usando datos mock (sin depender del MS de bikes ni de RabbitMQ)."""

from tests.mock_bike_locations import MOCK_BIKE_LOCATIONS


class TestAvailableLocationsWithMockSeed:
    def test_returns_only_available_mock_bikes(self, client, seeded_mock_bike_locations):
        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        data = response.get_json()

        expected_available = [row for row in MOCK_BIKE_LOCATIONS if row[3] == "available"]
        assert len(data) == len(expected_available)

        returned_ids = {item["bikeId"] for item in data}
        assert returned_ids == {row[0] for row in expected_available}

        for item in data:
            assert set(item.keys()) == {"bikeId", "latitude", "longitude"}
            assert isinstance(item["latitude"], (int, float))
            assert isinstance(item["longitude"], (int, float))

    def test_mock_unavailable_bike_not_listed(self, client, seeded_mock_bike_locations):
        response = client.get("/api/v1/locations/available")
        data = response.get_json()
        ids = {item["bikeId"] for item in data}
        assert "BIKE-MOCK-003" not in ids

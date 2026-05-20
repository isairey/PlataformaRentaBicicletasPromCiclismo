from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from werkzeug.exceptions import NotFound

from app.models.bike import Bike, BikeState, BikeType
from app.schemas.bike import BikeCreate, BikeListResponse, BikeResponse, BikeUpdate
from app.services.bike_service import BikeService


def _fake_bike(**overrides):
    defaults = {
        "id": "test-uuid",
        "brand": "Trek",
        "type": BikeType.Mountain,
        "colour": "Red",
        "state": BikeState.Free,
    }
    defaults.update(overrides)
    bike = MagicMock(spec=Bike)
    for k, v in defaults.items():
        setattr(bike, k, v)
    return bike


class TestCreateBike:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = BikeService(self.repo)

    def test_create_bike_success(self):
        data = BikeCreate(
            brand="Trek",
            type=BikeType.Mountain,
            colour="Red",
            latitude=6.2442,
            longitude=-75.5812,
        )
        self.repo.create.return_value = _fake_bike()

        result = self.service.create_bike(data)

        self.repo.create.assert_called_once_with(data)
        assert isinstance(result, BikeResponse)
        assert result.brand == "Trek"
        assert result.type == BikeType.Mountain
        assert result.state == BikeState.Free

    def test_create_bike_invalid_enum_raises_validation(self):
        with pytest.raises(ValidationError):
            BikeCreate(
                brand="Trek",
                type="BMX",
                colour="Red",
                latitude=6.2442,
                longitude=-75.5812,
            )


class TestGetBike:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = BikeService(self.repo)

    def test_get_bike_success(self, app):
        self.repo.get_by_id.return_value = _fake_bike()
        with app.app_context():
            result = self.service.get_bike("test-uuid")
        assert isinstance(result, BikeResponse)
        assert result.id == "test-uuid"

    def test_get_bike_not_found_raises_404(self, app):
        self.repo.get_by_id.return_value = None
        with app.app_context():
            with pytest.raises(NotFound):
                self.service.get_bike("missing-id")


class TestListBikes:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = BikeService(self.repo)

    def test_list_bikes_returns_list_response(self, app):
        self.repo.list.return_value = ([_fake_bike()], 1)
        with app.app_context():
            result = self.service.list_bikes(state=None, bike_type=None, page=1, page_size=20)
        assert isinstance(result, BikeListResponse)
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.bikes) == 1

    def test_list_bikes_passes_filters_to_repo(self, app):
        self.repo.list.return_value = ([], 0)
        with app.app_context():
            self.service.list_bikes(state=BikeState.Free, bike_type=BikeType.Mountain, page=2, page_size=10)
        self.repo.list.assert_called_once_with(
            state=BikeState.Free, bike_type=BikeType.Mountain, offset=10, limit=10
        )


class TestUpdateBike:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = BikeService(self.repo)

    def test_update_bike_success(self, app):
        updated = _fake_bike(state=BikeState.Rented)
        self.repo.update.return_value = updated
        data = BikeUpdate(state=BikeState.Rented)
        with app.app_context():
            result = self.service.update_bike("test-uuid", data)
        assert isinstance(result, BikeResponse)
        assert result.state == BikeState.Rented

    def test_update_bike_not_found_raises_404(self, app):
        self.repo.update.return_value = None
        data = BikeUpdate(colour="Blue")
        with app.app_context():
            with pytest.raises(NotFound):
                self.service.update_bike("missing-id", data)

    def test_update_partial_only_provided_fields(self, app):
        updated = _fake_bike(colour="Blue")
        self.repo.update.return_value = updated
        data = BikeUpdate(colour="Blue")
        with app.app_context():
            result = self.service.update_bike("test-uuid", data)
        assert result.colour == "Blue"


class TestDeleteBike:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = BikeService(self.repo)

    def test_delete_bike_success(self, app):
        self.repo.delete.return_value = True
        with app.app_context():
            self.service.delete_bike("test-uuid")
        self.repo.delete.assert_called_once_with("test-uuid")

    def test_delete_bike_not_found_raises_404(self, app):
        self.repo.delete.return_value = False
        with app.app_context():
            with pytest.raises(NotFound):
                self.service.delete_bike("missing-id")

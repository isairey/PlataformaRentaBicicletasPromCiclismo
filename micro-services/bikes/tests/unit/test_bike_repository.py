from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from app.models.bike import Bike, BikeState, BikeType
from app.repositories.bike_repository import BikeRepository
from app.schemas.bike import BikeCreate, BikeUpdate


@pytest.fixture
def mock_db():
    with patch("app.repositories.bike_repository.db") as mock:
        yield mock


@pytest.fixture
def repo():
    return BikeRepository()


class TestCreate:
    def test_create_adds_and_commits(self, repo, mock_db):
        data = BikeCreate(
            brand="Trek",
            type=BikeType.Mountain,
            colour="Red",
            latitude=6.2442,
            longitude=-75.5812,
        )
        result = repo.create(data)

        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        assert isinstance(result, Bike)
        assert result.brand == "Trek"
        assert result.type == BikeType.Mountain
        assert result.colour == "Red"
        assert result.state == BikeState.Free


class TestGetById:
    def test_get_by_id_found(self, repo, mock_db):
        fake_bike = MagicMock(spec=Bike)
        mock_db.session.get.return_value = fake_bike

        result = repo.get_by_id("some-uuid")

        mock_db.session.get.assert_called_once_with(Bike, "some-uuid")
        assert result is fake_bike

    def test_get_by_id_not_found(self, repo, mock_db):
        mock_db.session.get.return_value = None
        result = repo.get_by_id("missing")
        assert result is None


class TestList:
    def test_list_no_filters(self, repo, mock_db):
        fake_bike = MagicMock(spec=Bike)
        mock_db.session.scalar.return_value = 1
        mock_db.session.scalars.return_value = [fake_bike]

        bikes, total = repo.list()

        assert total == 1
        assert len(bikes) == 1

    def test_list_with_state_filter(self, repo, mock_db):
        mock_db.session.scalar.return_value = 0
        mock_db.session.scalars.return_value = []

        bikes, total = repo.list(state=BikeState.Free)

        assert total == 0
        assert bikes == []

    def test_list_with_type_filter(self, repo, mock_db):
        mock_db.session.scalar.return_value = 0
        mock_db.session.scalars.return_value = []

        bikes, total = repo.list(bike_type=BikeType.Mountain)

        assert total == 0


class TestUpdate:
    def test_update_found(self, repo, mock_db):
        fake_bike = MagicMock(spec=Bike)
        fake_bike.colour = "Red"
        mock_db.session.get.return_value = fake_bike

        data = BikeUpdate(colour="Blue")
        result = repo.update("some-uuid", data)

        assert result is fake_bike
        mock_db.session.commit.assert_called_once()

    def test_update_not_found(self, repo, mock_db):
        mock_db.session.get.return_value = None

        data = BikeUpdate(colour="Blue")
        result = repo.update("missing", data)

        assert result is None
        mock_db.session.commit.assert_not_called()


class TestDelete:
    def test_delete_found(self, repo, mock_db):
        fake_bike = MagicMock(spec=Bike)
        mock_db.session.get.return_value = fake_bike

        result = repo.delete("some-uuid")

        assert result is True
        mock_db.session.delete.assert_called_once_with(fake_bike)
        mock_db.session.commit.assert_called_once()

    def test_delete_not_found(self, repo, mock_db):
        mock_db.session.get.return_value = None

        result = repo.delete("missing")

        assert result is False
        mock_db.session.delete.assert_not_called()

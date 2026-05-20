import pytest

from app import create_app, db as _db
from app import auth as auth_module
from app.config import TestingConfig
from app.models.location import BikeLocation, LocationStatus
from tests.mock_bike_locations import MOCK_BIKE_LOCATIONS


@pytest.fixture(scope="session")
def app():
    test_config = TestingConfig()
    test_config.SQLALCHEMY_DATABASE_URI = "sqlite://"
    _app = create_app(test_config)
    return _app


@pytest.fixture(autouse=True)
def db_session(app):
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture()
def client(app):
    test_client = app.test_client()
    # Map endpoints are protected by @require_authentication
    test_client.environ_base["HTTP_AUTHORIZATION"] = "Bearer admin-token"
    return test_client


@pytest.fixture(autouse=True)
def mock_verify_token(monkeypatch):

    def fake_verify_token(token: str) -> dict:
        # The application only needs claims to exist.
        return {
            "uid": "test-user",
            "email": "test@example.com",
            "role": "user",
            "admin": False,
        }

    monkeypatch.setattr(auth_module, "verify_token", fake_verify_token)


@pytest.fixture()
def seeded_mock_bike_locations(app, db_session):
    """Inserta bicis mock en la BD (vacía al inicio de cada test por db_session)."""
    for bike_id, lat, lon, status_str in MOCK_BIKE_LOCATIONS:
        db_session.add(
            BikeLocation(
                bike_id=bike_id,
                latitude=lat,
                longitude=lon,
                status=LocationStatus(status_str),
            )
        )
    db_session.commit()

import pytest

from app import create_app, db as _db
from app.config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create the Flask application for the test session."""
    test_config = TestingConfig()
    test_config.SQLALCHEMY_DATABASE_URI = "sqlite://"
    _app = create_app(test_config)
    return _app


@pytest.fixture(autouse=True)
def db_session(app):
    """Create tables before each test and drop after."""
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()

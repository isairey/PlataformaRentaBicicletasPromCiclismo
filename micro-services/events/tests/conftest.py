import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app import auth as auth_module
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_token(app):
    return "admin-token"


@pytest.fixture
def user_token(app):
    return "user-token"


@pytest.fixture(autouse=True)
def mock_verify_token(monkeypatch):
    def fake_verify_token(token: str) -> dict:
        if token == "admin-token":
            return {
                "uid": "admin-user",
                "email": "admin@example.com",
                "role": "admin",
                "admin": True,
            }
        if token == "user-token":
            return {
                "uid": "normal-user",
                "email": "user@example.com",
                "role": "user",
                "admin": False,
            }
        raise ValueError("Invalid authentication token")

    monkeypatch.setattr(auth_module, "verify_token", fake_verify_token)

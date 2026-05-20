import importlib
import os
import sys
from pathlib import Path

import firebase_admin
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def app_module(monkeypatch):
    env_vars = {
        "FIREBASE_TYPE": "service_account",
        "FIREBASE_PROJECT_ID": "test-project",
        "FIREBASE_PRIVATE_KEY_ID": "test-key-id",
        "FIREBASE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\\ntest\\n-----END PRIVATE KEY-----\\n",
        "FIREBASE_CLIENT_EMAIL": "firebase-adminsdk@test-project.iam.gserviceaccount.com",
        "FIREBASE_CLIENT_ID": "123456789",
        "FIREBASE_CLIENT_X509_CERT_URL": "https://example.com/cert.pem",
        "FIREBASE_WEB_API_KEY": "test-web-api-key",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    monkeypatch.setattr(firebase_admin, "_apps", [object()])

    if "app" in sys.modules:
        module = importlib.reload(sys.modules["app"])
    else:
        module = importlib.import_module("app")

    module.app.config["TESTING"] = True
    yield module

    sys.modules.pop("app", None)


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()

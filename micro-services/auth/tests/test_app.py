from types import SimpleNamespace

from google.auth.exceptions import RefreshError


def test_health_endpoint_reports_firebase_configuration(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "firebaseConfigured": True,
    }


def test_register_returns_validation_errors_for_invalid_payload(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "bad-email", "password": "123", "name": ""},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "VALIDATION_ERROR",
        "details": [
            "Invalid email format",
            "Password must be at least 8 chars",
            "Name is required",
        ],
    }


def test_register_creates_user_and_sets_admin_claims(client, app_module, monkeypatch):
    created_user = SimpleNamespace(uid="user-123", email="admin@example.com")

    create_user_calls = {}
    claims_calls = {}

    def fake_create_user(**kwargs):
        create_user_calls.update(kwargs)
        return created_user

    def fake_set_custom_user_claims(uid, claims):
        claims_calls["uid"] = uid
        claims_calls["claims"] = claims

    monkeypatch.setattr(app_module.auth, "create_user", fake_create_user)
    monkeypatch.setattr(app_module.auth, "set_custom_user_claims", fake_set_custom_user_claims)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "supersecure",
            "name": "Admin User",
            "role": "admin",
        },
    )

    body = response.get_json()

    assert response.status_code == 201
    assert body["uid"] == "user-123"
    assert body["email"] == "admin@example.com"
    assert "createdAt" in body
    assert create_user_calls == {
        "email": "admin@example.com",
        "password": "supersecure",
        "display_name": "Admin User",
        "disabled": False,
    }
    assert claims_calls == {
        "uid": "user-123",
        "claims": {
            "role": "admin",
            "admin": True,
        },
    }


def test_register_returns_conflict_when_email_already_exists(client, app_module, monkeypatch):
    class FakeEmailAlreadyExistsError(Exception):
        pass

    monkeypatch.setattr(app_module.auth, "EmailAlreadyExistsError", FakeEmailAlreadyExistsError)

    def fake_create_user(**kwargs):
        raise FakeEmailAlreadyExistsError("already exists")

    monkeypatch.setattr(app_module.auth, "create_user", fake_create_user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "supersecure",
            "name": "User",
        },
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "EMAIL_ALREADY_EXISTS"


def test_register_returns_configuration_error_when_firebase_credentials_fail(client, app_module, monkeypatch):
    def fake_create_user(**kwargs):
        raise RefreshError("invalid JWT signature")

    monkeypatch.setattr(app_module.auth, "create_user", fake_create_user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "supersecure",
            "name": "User",
        },
    )

    body = response.get_json()

    assert response.status_code == 500
    assert body["error"] == "FIREBASE_CONFIGURATION_ERROR"


def test_login_requires_web_api_key(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "AUTH_LOGIN_URL", None)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "supersecure"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "CONFIGURATION_ERROR"


def test_login_validates_required_fields(client):
    response = client.post("/api/v1/auth/login", json={"email": "user@example.com"})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "VALIDATION_ERROR",
        "details": ["Email and password required"],
    }


def test_login_returns_tokens_on_success(client, app_module, monkeypatch):
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {
                "localId": "firebase-user",
                "idToken": "token-123",
                "refreshToken": "refresh-123",
                "expiresIn": "3600",
            }

    def fake_post(url, json, timeout):
        assert url == app_module.AUTH_LOGIN_URL
        assert json == {
            "email": "user@example.com",
            "password": "supersecure",
            "returnSecureToken": True,
        }
        assert timeout == 30
        return FakeResponse()

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "supersecure"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "idToken": "token-123",
        "refreshToken": "refresh-123",
        "expiresIn": 3600,
    }


def test_login_maps_invalid_password_error(client, app_module, monkeypatch):
    class FakeResponse:
        status_code = 400

        @staticmethod
        def json():
            return {"error": {"message": "INVALID_PASSWORD"}}

    monkeypatch.setattr(app_module.requests, "post", lambda *args, **kwargs: FakeResponse())

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "INVALID_CREDENTIALS"


def test_logout_requires_bearer_token(client):
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 401
    assert response.get_json()["error"] == "UNAUTHORIZED"


def test_logout_returns_unauthorized_for_invalid_token(client, app_module, monkeypatch):
    def fake_verify_id_token(token):
        raise ValueError("bad token")

    monkeypatch.setattr(app_module.auth, "verify_id_token", fake_verify_id_token)

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "UNAUTHORIZED"


def test_logout_revokes_tokens_for_authenticated_user(client, app_module, monkeypatch):
    revoke_calls = {}

    monkeypatch.setattr(
        app_module.auth,
        "verify_id_token",
        lambda token: {"uid": "firebase-user"},
    )

    def fake_revoke_refresh_tokens(uid):
        revoke_calls["uid"] = uid

    monkeypatch.setattr(app_module.auth, "revoke_refresh_tokens", fake_revoke_refresh_tokens)

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Session revoked successfully"}
    assert revoke_calls == {"uid": "firebase-user"}

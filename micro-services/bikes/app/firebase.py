import firebase_admin
from firebase_admin import auth, credentials


def initialize_firebase(app) -> None:
    if firebase_admin._apps:
        return

    certificate_data = {
        "type": app.config["FIREBASE_TYPE"],
        "project_id": app.config["FIREBASE_PROJECT_ID"],
        "private_key_id": app.config["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": app.config["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": app.config["FIREBASE_CLIENT_EMAIL"],
        "client_id": app.config["FIREBASE_CLIENT_ID"],
        "auth_uri": app.config["FIREBASE_AUTH_URI"],
        "token_uri": app.config["FIREBASE_TOKEN_URI"],
        "auth_provider_x509_cert_url": app.config["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": app.config["FIREBASE_CLIENT_X509_CERT_URL"],
        "universe_domain": app.config["FIREBASE_UNIVERSE_DOMAIN"],
    }

    required_fields = [
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "client_x509_cert_url",
    ]
    missing_fields = [field for field in required_fields if not certificate_data[field]]
    if missing_fields:
        if app.config.get("TESTING"):
            return
        missing_env_vars = ", ".join(f"FIREBASE_{field.upper()}" for field in missing_fields)
        raise RuntimeError(
            f"Firebase environment variables are missing: {missing_env_vars}."
        )

    firebase_admin.initialize_app(credentials.Certificate(certificate_data))


def verify_token(token: str) -> dict:
    try:
        return auth.verify_id_token(token)
    except Exception as exc:
        raise ValueError("Invalid authentication token") from exc

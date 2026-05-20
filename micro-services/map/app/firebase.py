import os

import firebase_admin
from firebase_admin import auth, credentials


def initialize_firebase(app) -> None:
    if firebase_admin._apps:
        return

    if app.config.get("TESTING"):
        # Tests mock verify_token; avoid failing due to missing env vars.
        return

    required_env_vars = [
        "FIREBASE_TYPE",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_AUTH_URI",
        "FIREBASE_TOKEN_URI",
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
        "FIREBASE_CLIENT_X509_CERT_URL",
        "FIREBASE_UNIVERSE_DOMAIN",
    ]
    missing = [k for k in required_env_vars if not os.environ.get(k)]
    if missing:
        raise RuntimeError(
            "Missing Firebase environment variables: "
            + ", ".join(missing[:6])
            + ("..." if len(missing) > 6 else "")
        )

    certificate_data = {
        "type": os.environ["FIREBASE_TYPE"],
        "project_id": os.environ["FIREBASE_PROJECT_ID"],
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "auth_uri": os.environ["FIREBASE_AUTH_URI"],
        "token_uri": os.environ["FIREBASE_TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
        "universe_domain": os.environ["FIREBASE_UNIVERSE_DOMAIN"],
    }

    firebase_admin.initialize_app(credentials.Certificate(certificate_data))


def verify_token(token: str) -> dict:
    return auth.verify_id_token(token)


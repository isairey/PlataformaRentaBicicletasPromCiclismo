import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    PORT = int(os.environ.get("PORT", 8080))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_REPLY_TIMEOUT = int(os.environ.get("RABBITMQ_REPLY_TIMEOUT", 10))
    RABBITMQ_ENABLED = os.environ.get("RABBITMQ_ENABLED", "true").lower() == "true"
    FIREBASE_TYPE = os.environ.get("FIREBASE_TYPE", "service_account")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY_ID = os.environ.get("FIREBASE_PRIVATE_KEY_ID", "")
    FIREBASE_PRIVATE_KEY = os.environ.get("FIREBASE_PRIVATE_KEY", "")
    FIREBASE_CLIENT_EMAIL = os.environ.get("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_CLIENT_ID = os.environ.get("FIREBASE_CLIENT_ID", "")
    FIREBASE_AUTH_URI = os.environ.get(
        "FIREBASE_AUTH_URI",
        "https://accounts.google.com/o/oauth2/auth",
    )
    FIREBASE_TOKEN_URI = os.environ.get(
        "FIREBASE_TOKEN_URI",
        "https://oauth2.googleapis.com/token",
    )
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL = os.environ.get(
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
        "https://www.googleapis.com/oauth2/v1/certs",
    )
    FIREBASE_CLIENT_X509_CERT_URL = os.environ.get("FIREBASE_CLIENT_X509_CERT_URL", "")
    FIREBASE_UNIVERSE_DOMAIN = os.environ.get("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///test.db")
    RABBITMQ_ENABLED = False

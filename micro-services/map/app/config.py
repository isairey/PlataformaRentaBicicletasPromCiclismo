import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    PORT = int(os.environ.get("PORT", 8081))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE", "bike_network.events")
    RABBITMQ_ROUTING_KEY_BIKE_CREATED = os.environ.get(
        "RABBITMQ_ROUTING_KEY_BIKE_CREATED", "bike.created"
    )
    RABBITMQ_ROUTING_KEY_BIKE_DELETED = os.environ.get(
        "RABBITMQ_ROUTING_KEY_BIKE_DELETED", "bike.deleted"
    )
    RABBITMQ_ROUTING_KEY_RENTAL_COMPLETED = os.environ.get(
        "RABBITMQ_ROUTING_KEY_RENTAL_COMPLETED", "rental.completed"
    )
    RABBITMQ_ROUTING_KEY_BIKE_STATUS_UPDATED = os.environ.get(
        "RABBITMQ_ROUTING_KEY_BIKE_STATUS_UPDATED", "bike.statusUpdated"
    )
    ENABLE_RABBIT_CONSUMERS = os.environ.get("ENABLE_RABBIT_CONSUMERS", "").lower() in (
        "1",
        "true",
        "yes",
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///test.db")
    ENABLE_RABBIT_CONSUMERS = False

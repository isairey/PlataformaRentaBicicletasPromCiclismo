import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    SQLALCHEMY_DATABASE_URI      = os.getenv("MYSQL_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RabbitMQ
    RABBITMQ_URL         = os.getenv("RABBITMQ_URL")
    RABBITMQ_EXCHANGE    = os.getenv("RABBITMQ_EXCHANGE")
    RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY")

    # Bike CRUD microservice
    BIKE_SERVICE_URL = os.getenv("BIKE_SERVICE_URL")

    # Firebase
    FIREBASE_TYPE                        = os.getenv("FIREBASE_TYPE", "service_account")
    FIREBASE_PROJECT_ID                  = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID              = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY                 = os.getenv("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL                = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID                   = os.getenv("FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI                    = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    FIREBASE_TOKEN_URI                   = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
    FIREBASE_CLIENT_X509_CERT_URL        = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    FIREBASE_UNIVERSE_DOMAIN             = os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
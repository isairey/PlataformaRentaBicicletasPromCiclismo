from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        from app.config import Config

        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import location  # noqa: F401

    from app.errors import register_error_handlers

    register_error_handlers(app)

    from app.routes.queries.health import health_bp
    from app.routes.queries.locations import locations_queries_bp

    # Optional Firebase authentication (used to protect read endpoints).
    from app.auth import ensure_firebase_initialized
    ensure_firebase_initialized(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(locations_queries_bp)

    from app.messaging.runner import register_consumers

    register_consumers(app)

    from app.seeding.cli import register_seed_commands

    register_seed_commands(app)

    return app

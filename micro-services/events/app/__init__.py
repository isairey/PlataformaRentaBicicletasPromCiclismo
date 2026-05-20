import time

from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .config import config_by_name
from .errors import register_error_handlers
from .extensions import db
from .firebase import initialize_firebase
from .models import Competition, Event, Route
from .routes import register_blueprints


def _wait_for_database(max_retries: int = 10, delay_seconds: int = 3) -> None:
    for attempt in range(1, max_retries + 1):
        try:
            db.session.execute(text("SELECT 1"))
            return
        except OperationalError:
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)


def _ensure_competitions_schema() -> None:
    if db.engine.dialect.name != "mysql":
        return

    table_exists = db.session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = 'competitions'
            """
        )
    ).scalar_one()

    if not table_exists:
        return

    columns_result = db.session.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = 'competitions'
            """
        )
    )
    columns = {row[0] for row in columns_result}

    if "created_at" not in columns:
        db.session.execute(
            text(
                """
                ALTER TABLE competitions
                ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                """
            )
        )

    if "updated_at" not in columns:
        db.session.execute(
            text(
                """
                ALTER TABLE competitions
                ADD COLUMN updated_at TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
                """
            )
        )

    db.session.commit()


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    selected_config = config_name or "default"
    app.config.from_object(config_by_name[selected_config])

    initialize_firebase(app)
    CORS(app)
    db.init_app(app)
    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        _wait_for_database()
        _ = Competition
        _ = Event
        _ = Route
        db.create_all()
        _ensure_competitions_schema()

    return app

import os
import time
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from app.config import Config

db = SQLAlchemy()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    with app.app_context():
        from app.models.rental import Rental

        if not app.config.get("TESTING") and os.environ.get("TESTING") != "true":
            _wait_for_db(app)
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS rentals (
                        rental_id  VARCHAR(36)  NOT NULL,
                        user_id    VARCHAR(36)  NOT NULL,
                        bike_id    VARCHAR(36)  NOT NULL,
                        start_time DATETIME     NOT NULL,
                        end_time   DATETIME     NULL,
                        status     VARCHAR(20)  NOT NULL,
                        PRIMARY KEY (rental_id)
                    )
                """))
                conn.commit()
                try:
                    conn.execute(text(
                        "ALTER TABLE rentals ADD COLUMN end_time DATETIME NULL"
                    ))
                    conn.commit()
                    logger.info("Columna end_time agregada.")
                except Exception:
                    conn.rollback()
            logger.info("Tabla rentals lista.")
        else:
            db.create_all()

        from app.auth.firebase import initialize_firebase
        initialize_firebase(app)

    from app.routes.rental_routes import rental_bp
    app.register_blueprint(rental_bp)

    return app


def _wait_for_db(app, retries=10, delay=3):
    for attempt in range(1, retries + 1):
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("Conexión a MySQL exitosa.")
            return
        except Exception as e:
            logger.warning(f"MySQL no disponible (intento {attempt}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("No se pudo conectar a MySQL después de varios intentos.")
import logging
from datetime import datetime, timezone
from app import db
from app.models.rental import Rental
from app.services.bike_service import get_bike
from app.messaging.publisher import publish_rental_started, publish_rental_ended

logger = logging.getLogger(__name__)


def create_rental(user_id: str, bike_id: str) -> dict:
    # 1. Verificar que la bici existe
    bike = get_bike(bike_id)
    if bike is None:
        raise BikeNotFoundException(f"Bici {bike_id} no encontrada.")

    # 2. Verificar que la bici está disponible
    if not bike.get("available", False):
        raise BikeUnavailableException(f"Bici {bike_id} no está disponible.")

    # 3. Crear el registro de renta en MySQL
    rental = Rental(user_id=user_id, bike_id=bike_id)
    db.session.add(rental)
    db.session.commit()
    logger.info(f"Rental creado: {rental.rental_id}")

    # 4. Publicar evento rental.started a RabbitMQ
    try:
        publish_rental_started(rental.to_dict())
    except Exception as e:
        db.session.delete(rental)
        db.session.commit()
        logger.error(f"Rollback rental {rental.rental_id} por fallo en RabbitMQ: {e}")
        raise

    return rental.to_dict()


def return_rental(rental_id: str) -> dict:
    # 1. Buscar el rental
    rental = Rental.query.get(rental_id)
    if rental is None:
        raise RentalNotFoundException(f"Rental {rental_id} no encontrado.")

    # 2. Verificar que no esté ya completado
    if rental.status == "COMPLETED":
        raise RentalAlreadyCompletedException(f"Rental {rental_id} ya fue completado.")

    # 3. Cerrar el rental
    rental.status   = "COMPLETED"
    rental.end_time = datetime.now(timezone.utc)
    db.session.commit()
    logger.info(f"Rental completado: {rental.rental_id}")

    # 4. Publicar evento rental.ended a RabbitMQ
    try:
        publish_rental_ended(rental.to_dict())
    except Exception as e:
        # Rollback: revertir el cierre del rental
        rental.status   = "ACTIVE"
        rental.end_time = None
        db.session.commit()
        logger.error(f"Rollback return {rental.rental_id} por fallo en RabbitMQ: {e}")
        raise

    return rental.to_dict()


def get_rentals_by_user(user_id: str) -> list[dict]:
    rentals = Rental.query.filter_by(user_id=user_id).all()
    return [r.to_dict() for r in rentals]


# Excepciones propias del dominio
class BikeNotFoundException(Exception):
    pass

class BikeUnavailableException(Exception):
    pass

class RentalNotFoundException(Exception):
    pass

class RentalAlreadyCompletedException(Exception):
    pass

class RentalServiceError(Exception):
    pass
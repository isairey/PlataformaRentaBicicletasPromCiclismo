import logging
from flask import current_app
from app.messaging.publisher import check_bike_available  # ← nuevo import

logger = logging.getLogger(__name__)

def get_bike(bike_id: str) -> dict:
    """
    Consulta disponibilidad de la bici via RPC sobre RabbitMQ.
    Retorna un dict con 'available' o None si no responde.
    """
    try:
        available = check_bike_available(bike_id)
        return {"available": available}

    except TimeoutError:
        logger.error(f"Timeout RPC consultando bike {bike_id}")
        return None

    except Exception as e:
        logger.error(f"Error RPC consultando bike {bike_id}: {e}")
        raise
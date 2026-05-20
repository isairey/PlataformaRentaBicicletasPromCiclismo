from flask import Blueprint, request, jsonify, g
from app.auth.decorators import require_authentication
from app.services.rental_service import (
    create_rental,
    return_rental,
    get_rentals_by_user,
    BikeNotFoundException,
    BikeUnavailableException,
    RentalNotFoundException,
    RentalAlreadyCompletedException,
)

rental_bp = Blueprint("rental", __name__)


@rental_bp.route("/api/v1/rental", methods=["POST"])
@require_authentication
def create_rental_route():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "El body debe ser JSON válido."}), 400

    bike_id = data.get("bikeId")

    if not bike_id:
        return jsonify({"error": "bikeId es requerido."}), 400

    if not isinstance(bike_id, str):
        return jsonify({"error": "bikeId debe ser un string."}), 400

    if not bike_id.strip():
        return jsonify({"error": "bikeId no puede estar vacío."}), 400

    user_id = g.current_user["uid"]

    try:
        rental = create_rental(user_id=user_id, bike_id=bike_id)
        return jsonify(rental), 201

    except BikeNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    except BikeUnavailableException as e:
        return jsonify({"error": str(e)}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor."}), 500


@rental_bp.route("/api/v1/rental/user/<string:user_id>", methods=["GET"])
@require_authentication
def get_user_rentals_route(user_id):
    if g.current_user["uid"] != user_id:
        return jsonify({"error": "No autorizado para ver las rentas de este usuario."}), 403

    try:
        rentals = get_rentals_by_user(user_id=user_id)
        return jsonify(rentals), 200

    except Exception:
        return jsonify({"error": "Error interno del servidor."}), 500


@rental_bp.route("/api/v1/rental/<string:rental_id>/return", methods=["PATCH"])
@require_authentication
def return_rental_route(rental_id):

    if not rental_id or not rental_id.strip():
        return jsonify({"error": "rentalId inválido."}), 400

    try:
        rental = return_rental(rental_id=rental_id)
        return jsonify(rental), 200

    except RentalNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    except RentalAlreadyCompletedException as e:
        return jsonify({"error": str(e)}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor."}), 500
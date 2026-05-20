from unittest.mock import patch
import pytest
import pytest
from app.models.rental import Rental
from app import db
from app.services.rental_service import (
    RentalNotFoundException,
    RentalAlreadyCompletedException,
    RentalServiceError,
)

@pytest.fixture
def rental(app):
    with app.app_context():
        rental = Rental(
            rental_id="rental-001",
            bike_id="bike-001",
            user_id="user-123",
            status="ACTIVE"
        )
        db.session.add(rental)
        db.session.commit()
        yield rental
        db.session.delete(rental)
        db.session.commit()

def test_return_rental_success(client, rental):
    # Parchea la función en el módulo de rutas
    with patch("app.routes.rental_routes.return_rental") as mock_return:
        mock_return.return_value = {
            "rentalId": "rental-001",
            "bikeId": "bike-001",
            "userId": "user-123",
            "status": "COMPLETED"
        }
        response = client.patch("/api/v1/rental/rental-001/return", json={"userId": "user-123"})
        assert response.status_code == 200

def test_return_rental_not_found(client):
    with patch("app.routes.rental_routes.return_rental") as mock_return:
        mock_return.side_effect = RentalNotFoundException("Rental not found")
        response = client.patch("/api/v1/rental/rental-999/return", json={"userId": "user-123"})
        assert response.status_code == 404

def test_return_rental_already_completed(client, rental):
    with patch("app.routes.rental_routes.return_rental") as mock_return:
        mock_return.side_effect = RentalAlreadyCompletedException("Rental already completed")
        response = client.patch("/api/v1/rental/rental-001/return", json={"userId": "user-123"})
        assert response.status_code == 409

def test_return_rental_internal_error(client, rental):
    with patch("app.routes.rental_routes.return_rental") as mock_return:
        mock_return.side_effect = RentalServiceError("Unexpected error")
        response = client.patch("/api/v1/rental/rental-001/return", json={"userId": "user-123"})
        assert response.status_code == 500
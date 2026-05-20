from flask import abort

from app.models.bike import BikeState, BikeType
from app.repositories.bike_repository import BikeRepository
from app.schemas.bike import (
    BikeCreate,
    BikeListResponse,
    BikeResponse,
    BikeUpdate,
)
from app.utils.pagination import parse_pagination


class BikeService:
    def __init__(self, repository: BikeRepository):
        self.repository = repository

    def create_bike(self, data: BikeCreate) -> BikeResponse:
        bike = self.repository.create(data)
        return BikeResponse.model_validate(bike)

    def get_bike(self, bike_id: str) -> BikeResponse:
        bike = self.repository.get_by_id(bike_id)
        if bike is None:
            abort(404, description=f"No bike found with id {bike_id}.")
        return BikeResponse.model_validate(bike)

    def list_bikes(
        self,
        state: BikeState | None,
        bike_type: BikeType | None,
        page: int,
        page_size: int,
    ) -> BikeListResponse:
        offset = (page - 1) * page_size
        bikes, total = self.repository.list(
            state=state, bike_type=bike_type, offset=offset, limit=page_size
        )
        return BikeListResponse(
            bikes=[BikeResponse.model_validate(b) for b in bikes],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update_bike(self, bike_id: str, data: BikeUpdate) -> BikeResponse:
        bike = self.repository.update(bike_id, data)
        if bike is None:
            abort(404, description=f"No bike found with id {bike_id}.")
        return BikeResponse.model_validate(bike)

    def delete_bike(self, bike_id: str) -> None:
        deleted = self.repository.delete(bike_id)
        if not deleted:
            abort(404, description=f"No bike found with id {bike_id}.")

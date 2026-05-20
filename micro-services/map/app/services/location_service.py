from app.repositories.location_repository import LocationRepository
from app.schemas.location import AvailableLocationItem


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

    def list_available_for_map(self) -> list[AvailableLocationItem]:
        rows = self.repository.list_available()
        return [AvailableLocationItem.model_validate(r) for r in rows]

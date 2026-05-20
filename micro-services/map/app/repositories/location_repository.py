from app import db
from app.models.location import BikeLocation, LocationStatus


class LocationRepository:
    def list_available(self) -> list[BikeLocation]:
        stmt = db.select(BikeLocation).where(BikeLocation.status == LocationStatus.available)
        return list(db.session.scalars(stmt))

    def get_by_bike_id(self, bike_id: str) -> BikeLocation | None:
        return db.session.get(BikeLocation, bike_id)

    def create_if_absent(self, bike_id: str, latitude: float, longitude: float) -> bool:
        """Returns ``True`` if a new row was inserted, ``False`` if it already existed
        (idempotent: no update).
        """
        if self.get_by_bike_id(bike_id) is not None:
            return False
        row = BikeLocation(
            bike_id=bike_id,
            latitude=latitude,
            longitude=longitude,
            status=LocationStatus.available,
        )
        db.session.add(row)
        db.session.commit()
        return True

    def update_status(self, bike_id: str, status: LocationStatus) -> bool:
        row = self.get_by_bike_id(bike_id)
        if row is None:
            return False
        row.status = status
        db.session.commit()
        return True

    def delete_by_bike_id(self, bike_id: str) -> bool:
        row = self.get_by_bike_id(bike_id)
        if row is None:
            return False
        db.session.delete(row)
        db.session.commit()
        return True

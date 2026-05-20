from app import db
from app.models.bike import Bike, BikeState, BikeType
from app.schemas.bike import BikeCreate, BikeUpdate


class BikeRepository:
    def create(self, data: BikeCreate) -> Bike:
        bike = Bike(
            brand=data.brand,
            type=data.type,
            colour=data.colour,
            state=data.state,
        )
        db.session.add(bike)
        db.session.commit()
        return bike

    def get_by_id(self, bike_id: str) -> Bike | None:
        return db.session.get(Bike, bike_id)

    def list(
        self,
        state: BikeState | None = None,
        bike_type: BikeType | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Bike], int]:
        query = db.select(Bike)
        if state is not None:
            query = query.where(Bike.state == state)
        if bike_type is not None:
            query = query.where(Bike.type == bike_type)

        total = db.session.scalar(
            db.select(db.func.count()).select_from(query.subquery())
        )
        bikes = list(db.session.scalars(query.offset(offset).limit(limit)))
        return bikes, total

    def update(self, bike_id: str, data: BikeUpdate) -> Bike | None:
        bike = self.get_by_id(bike_id)
        if bike is None:
            return None
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(bike, field, value)
        db.session.commit()
        return bike

    def delete(self, bike_id: str) -> bool:
        bike = self.get_by_id(bike_id)
        if bike is None:
            return False
        db.session.delete(bike)
        db.session.commit()
        return True

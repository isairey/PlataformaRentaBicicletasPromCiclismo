import enum
import uuid

from app import db


class BikeType(enum.Enum):
    Cross = "Cross"
    Mountain = "Mountain"
    Street = "Street"


class BikeState(enum.Enum):
    Rented = "Rented"
    Free = "Free"


class Bike(db.Model):
    __tablename__ = "bikes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(BikeType), nullable=False)
    colour = db.Column(db.String(50), nullable=False)
    state = db.Column(db.Enum(BikeState), nullable=False, default=BikeState.Free)

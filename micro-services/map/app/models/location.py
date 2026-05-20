import enum

from app import db


class LocationStatus(str, enum.Enum):
    available = "available"
    unavailable = "unavailable"


class BikeLocation(db.Model):
    __tablename__ = "locations"

    bike_id = db.Column(db.String(36), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(LocationStatus), nullable=False, default=LocationStatus.available)

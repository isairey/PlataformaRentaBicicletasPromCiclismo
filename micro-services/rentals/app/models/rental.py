from app import db
from datetime import datetime, timezone
import uuid

class Rental(db.Model):
    __tablename__ = "rentals"

    rental_id  = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36),  nullable=False)
    bike_id    = db.Column(db.String(36),  nullable=False)
    start_time = db.Column(db.DateTime,    nullable=False, default=lambda: datetime.now(timezone.utc))
    end_time   = db.Column(db.DateTime,    nullable=True)
    status     = db.Column(db.String(20),  nullable=False, default="ACTIVE")

    def to_dict(self):
        return {
            "rentalId":  self.rental_id,
            "userId":    self.user_id,
            "bikeId":    self.bike_id,
            "startTime": self.start_time.isoformat(),
            "endTime":   self.end_time.isoformat() if self.end_time else None,
            "status":    self.status,
        }
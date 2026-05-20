from pydantic import BaseModel, ConfigDict, Field


class AvailableLocationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bike_id: str = Field(serialization_alias="bikeId")
    latitude: float
    longitude: float

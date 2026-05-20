"""Reexporta el mismo dataset que el seeder CLI (`flask seed-locations`)."""

from app.seeding.location_seed_data import SEED_BIKE_LOCATIONS

MOCK_BIKE_LOCATIONS = SEED_BIKE_LOCATIONS

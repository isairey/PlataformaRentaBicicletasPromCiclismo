import click
from flask_migrate import upgrade
from sqlalchemy import inspect

from app import db
from app.models.location import BikeLocation, LocationStatus
from app.seeding.location_seed_data import SEED_BIKE_LOCATIONS


def _ensure_locations_table_exists():
    if not inspect(db.engine).has_table("locations"):
        click.echo("Aplicando migraciones (no existe la tabla locations)...")
        upgrade()


def register_seed_commands(app):
    @app.cli.command("seed-locations")
    @click.option(
        "--append",
        is_flag=True,
        help="No borrar la tabla; solo insertar filas cuyo bike_id aún no exista.",
    )
    def seed_locations_command(append):
        """Inserta bicis mock en ``locations`` para probar GET /api/v1/locations/available."""
        with app.app_context():
            _ensure_locations_table_exists()
            if not append:
                BikeLocation.query.delete()
                db.session.commit()
                click.echo("Tabla locations vaciada.")

            added = 0
            skipped = 0
            for bike_id, lat, lon, status_str in SEED_BIKE_LOCATIONS:
                if append and db.session.get(BikeLocation, bike_id):
                    click.echo(f"  Omitido (ya existe): {bike_id}")
                    skipped += 1
                    continue
                db.session.add(
                    BikeLocation(
                        bike_id=bike_id,
                        latitude=lat,
                        longitude=lon,
                        status=LocationStatus(status_str),
                    )
                )
                added += 1

            db.session.commit()
            click.echo(f"Listo: {added} filas insertadas, {skipped} omitidas.")

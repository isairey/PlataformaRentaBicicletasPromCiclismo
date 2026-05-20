"""create locations table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-28

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "locations",
        sa.Column("bike_id", sa.String(length=36), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("available", "unavailable", name="locationstatus"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("bike_id"),
    )


def downgrade():
    op.drop_table("locations")

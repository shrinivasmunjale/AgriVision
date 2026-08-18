"""add scan context to predictions

Revision ID: d93e1b5a8f24
Revises: c82d0a4f7e91
Create Date: 2026-08-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "d93e1b5a8f24"
down_revision = "c82d0a4f7e91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("predictions")}
    if "crop_age_days" not in columns:
        op.add_column("predictions", sa.Column("crop_age_days", sa.Integer(), nullable=True))
    if "life_stage" not in columns:
        op.add_column("predictions", sa.Column("life_stage", sa.String(length=50), nullable=True))


def downgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("predictions")}
    if "life_stage" in columns:
        op.drop_column("predictions", "life_stage")
    if "crop_age_days" in columns:
        op.drop_column("predictions", "crop_age_days")

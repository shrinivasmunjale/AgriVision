"""add evidence-backed recommendation tables

Revision ID: e14f6a2c9b10
Revises: d93e1b5a8f24
"""

from alembic import op
import sqlalchemy as sa


revision = "e14f6a2c9b10"
down_revision = "d93e1b5a8f24"
branch_labels = None
depends_on = None


def _source_columns():
    return [
        sa.Column("source_organization", sa.String(length=150), nullable=True),
        sa.Column("source_type", sa.String(length=120), nullable=True),
        sa.Column("source_document", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("evidence_note", sa.Text(), nullable=True),
        sa.Column("verified_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "disease_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_class", sa.String(length=150), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("crop", sa.String(length=50), nullable=False, server_default="Tomato"),
        sa.Column("recommendation_type", sa.String(length=80), nullable=True),
        sa.Column("active_ingredient", sa.String(length=200), nullable=True),
        sa.Column("formulation", sa.String(length=100), nullable=True),
        sa.Column("dose", sa.String(length=100), nullable=True),
        sa.Column("dose_unit", sa.String(length=50), nullable=True),
        sa.Column("water_volume", sa.String(length=100), nullable=True),
        sa.Column("application_method", sa.String(length=150), nullable=True),
        sa.Column("crop_stage", sa.String(length=200), nullable=True),
        sa.Column("frequency", sa.String(length=250), nullable=True),
        sa.Column("pre_harvest_interval", sa.String(length=100), nullable=True),
        sa.Column("re_entry_period", sa.String(length=100), nullable=True),
        *_source_columns(),
        sa.UniqueConstraint("model_class", "active_ingredient", "source_url", name="uq_disease_recommendation_source"),
    )
    op.create_index("idx_disease_recommendations_model_class", "disease_recommendations", ["model_class"])
    op.create_index("idx_disease_recommendations_active", "disease_recommendations", ["is_active"])

    op.create_table(
        "fertilizer_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("crop", sa.String(length=50), nullable=False, server_default="Tomato"),
        sa.Column("condition", sa.String(length=200), nullable=True),
        sa.Column("variety_type", sa.String(length=100), nullable=True),
        sa.Column("crop_stage", sa.String(length=150), nullable=True),
        sa.Column("nutrient", sa.String(length=100), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("dose", sa.String(length=100), nullable=True),
        sa.Column("dose_unit", sa.String(length=50), nullable=True),
        sa.Column("application_method", sa.String(length=150), nullable=True),
        *_source_columns(),
    )
    op.create_index("idx_fertilizer_recommendations_active", "fertilizer_recommendations", ["is_active"])


def downgrade() -> None:
    op.drop_index("idx_fertilizer_recommendations_active", table_name="fertilizer_recommendations")
    op.drop_table("fertilizer_recommendations")
    op.drop_index("idx_disease_recommendations_active", table_name="disease_recommendations")
    op.drop_index("idx_disease_recommendations_model_class", table_name="disease_recommendations")
    op.drop_table("disease_recommendations")
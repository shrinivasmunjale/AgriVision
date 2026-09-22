"""enhance fertilizer recommendations schema

Revision ID: a1b2c3d4e5f6
Revises: f2b4c8a1e3d5
"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "f2b4c8a1e3d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new fertilizer fields if they don't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("fertilizer_recommendations")]

    if "soil_test_required" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("soil_test_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    if "nitrogen_kg_ha" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("nitrogen_kg_ha", sa.Float(), nullable=True))
    if "phosphorus_kg_ha" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("phosphorus_kg_ha", sa.Float(), nullable=True))
    if "potassium_kg_ha" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("potassium_kg_ha", sa.Float(), nullable=True))
    if "fym_tonne_ha" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("fym_tonne_ha", sa.Float(), nullable=True))
    if "application_schedule" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("application_schedule", sa.Text(), nullable=True))
    if "evidence_level" not in columns:
        op.add_column("fertilizer_recommendations", sa.Column("evidence_level", sa.String(length=100), nullable=True))

    # Add indexes on variety and stage
    indexes = [ix["name"] for ix in inspector.get_indexes("fertilizer_recommendations")]
    if "idx_fertilizer_crop" not in indexes:
        op.create_index("idx_fertilizer_crop", "fertilizer_recommendations", ["crop"])
    if "idx_fertilizer_variety" not in indexes:
        op.create_index("idx_fertilizer_variety", "fertilizer_recommendations", ["variety_type"])
    if "idx_fertilizer_stage" not in indexes:
        op.create_index("idx_fertilizer_stage", "fertilizer_recommendations", ["crop_stage"])


def downgrade() -> None:
    op.drop_index("idx_fertilizer_stage", table_name="fertilizer_recommendations")
    op.drop_index("idx_fertilizer_variety", table_name="fertilizer_recommendations")
    op.drop_index("idx_fertilizer_crop", table_name="fertilizer_recommendations")
    op.drop_column("fertilizer_recommendations", "evidence_level")
    op.drop_column("fertilizer_recommendations", "application_schedule")
    op.drop_column("fertilizer_recommendations", "fym_tonne_ha")
    op.drop_column("fertilizer_recommendations", "potassium_kg_ha")
    op.drop_column("fertilizer_recommendations", "phosphorus_kg_ha")
    op.drop_column("fertilizer_recommendations", "nitrogen_kg_ha")
    op.drop_column("fertilizer_recommendations", "soil_test_required")

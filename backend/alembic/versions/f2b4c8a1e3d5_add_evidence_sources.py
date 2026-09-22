"""add evidence_sources table

Revision ID: f2b4c8a1e3d5
Revises: e14f6a2c9b10
"""

from alembic import op
import sqlalchemy as sa


revision = "f2b4c8a1e3d5"
down_revision = "e14f6a2c9b10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("source_type", sa.String(length=120), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("authority_level", sa.String(length=50), nullable=True),
        sa.Column("accessed_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_evidence_sources_active", "evidence_sources", ["is_active"])
    op.create_index("idx_evidence_sources_org", "evidence_sources", ["organization"])


def downgrade() -> None:
    op.drop_index("idx_evidence_sources_org", table_name="evidence_sources")
    op.drop_index("idx_evidence_sources_active", table_name="evidence_sources")
    op.drop_table("evidence_sources")

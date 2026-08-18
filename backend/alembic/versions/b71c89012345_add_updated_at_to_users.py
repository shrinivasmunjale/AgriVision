"""add_updated_at_to_users

Revision ID: b71c89012345
Revises: 4e523a9e8352
Create Date: 2026-08-18 18:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b71c89012345'
down_revision: Union[str, Sequence[str], None] = '4e523a9e8352'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'updated_at')

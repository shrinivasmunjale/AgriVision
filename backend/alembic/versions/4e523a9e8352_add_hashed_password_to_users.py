"""add_hashed_password_to_users

Revision ID: 4e523a9e8352
Revises: 9ac39e1a6db1
Create Date: 2026-07-17 00:53:13.907563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e523a9e8352'
down_revision: Union[str, Sequence[str], None] = '9ac39e1a6db1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add hashed_password column to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove hashed_password column from users table
    op.drop_column('users', 'hashed_password')

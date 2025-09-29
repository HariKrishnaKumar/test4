"""add_token_field_to_user_table

Revision ID: b2e4d81095fe
Revises: efa1b948e876
Create Date: 2025-09-15 19:43:48.497419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2e4d81095fe'
down_revision: Union[str, Sequence[str], None] = 'efa1b948e876'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add token field to users table
    op.add_column('users', sa.Column('token', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove token field from users table
    op.drop_column('users', 'token')

"""add_input_type_to_sessions_and_user_services

Revision ID: 34f7ee68ad56
Revises: ff16d163903b
Create Date: 2025-09-12 14:59:19.537868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34f7ee68ad56'
down_revision: Union[str, Sequence[str], None] = 'ff16d163903b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add input_type column to sessions table
    op.add_column('sessions', sa.Column('input_type', sa.String(10), nullable=True))

    # Add input_type column to user_services table
    op.add_column('user_services', sa.Column('input_type', sa.String(10), nullable=True))

    # Create indexes for better performance
    op.create_index('idx_sessions_input_type', 'sessions', ['input_type'])
    op.create_index('idx_user_services_input_type', 'user_services', ['input_type'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_user_services_input_type', table_name='user_services')
    op.drop_index('idx_sessions_input_type', table_name='sessions')

    # Drop columns
    op.drop_column('user_services', 'input_type')
    op.drop_column('sessions', 'input_type')

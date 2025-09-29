"""add_customer_id_to_carts_table

Revision ID: 681e95f11857
Revises: b2e4d81095fe
Create Date: 2025-09-16 17:27:59.594480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '681e95f11857'
down_revision: Union[str, Sequence[str], None] = 'b2e4d81095fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add customer_id column to carts table
    op.add_column('carts', sa.Column('customer_id', sa.Integer(), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_carts_customer_id',
        'carts', 'users',
        ['customer_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key constraint
    op.drop_constraint('fk_carts_customer_id', 'carts', type_='foreignkey')

    # Remove customer_id column
    op.drop_column('carts', 'customer_id')

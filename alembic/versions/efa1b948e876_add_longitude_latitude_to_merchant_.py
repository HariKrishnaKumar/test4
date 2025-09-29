"""add_longitude_latitude_to_merchant_detail

Revision ID: efa1b948e876
Revises: 34f7ee68ad56
Create Date: 2025-09-15 11:54:52.968728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efa1b948e876'
down_revision: Union[str, Sequence[str], None] = '34f7ee68ad56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add longitude and latitude columns to merchant_detail table
    op.add_column('merchant_detail', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('merchant_detail', sa.Column('latitude', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove longitude and latitude columns from merchant_detail table
    op.drop_column('merchant_detail', 'latitude')
    op.drop_column('merchant_detail', 'longitude')

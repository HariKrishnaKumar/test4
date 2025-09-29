"""add_services_and_user_services_tables

Revision ID: ff16d163903b
Revises: 0f77e2b58692
Create Date: 2025-09-12 14:26:12.896346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff16d163903b'
down_revision: Union[str, Sequence[str], None] = '0f77e2b58692'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create services table
    op.create_table('services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('service_name', sa.String(100), nullable=False),
        sa.Column('service_description', sa.String(255), nullable=True),
        sa.Column('is_active', sa.String(10), nullable=True, server_default=sa.text("'true'")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_name')
    )

    # Create user_services table
    op.create_table('user_services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('selected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index('idx_services_name', 'services', ['service_name'])
    op.create_index('idx_services_active', 'services', ['is_active'])
    op.create_index('idx_user_services_user', 'user_services', ['user_id'])
    op.create_index('idx_user_services_service', 'user_services', ['service_id'])
    op.create_index('idx_user_services_selected', 'user_services', ['selected_at'])

    # Insert default services
    op.execute("""
        INSERT INTO services (service_name, service_description, is_active) VALUES
        ('Delivery', 'Home delivery service - bringing food to your address', 'true'),
        ('Pickup', 'Self-pickup service - collect your order from our location', 'true'),
        ('Reservation', 'Table reservation service - book a table for dining in', 'true'),
        ('Catering', 'Catering service - food service for events and parties', 'true'),
        ('Events', 'Event planning service - special event food and service support', 'true')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_user_services_selected', table_name='user_services')
    op.drop_index('idx_user_services_service', table_name='user_services')
    op.drop_index('idx_user_services_user', table_name='user_services')
    op.drop_index('idx_services_active', table_name='services')
    op.drop_index('idx_services_name', table_name='services')

    # Drop tables
    op.drop_table('user_services')
    op.drop_table('services')

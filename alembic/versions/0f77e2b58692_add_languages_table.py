"""add_languages_table

Revision ID: 0f77e2b58692
Revises: 81431b1ca867
Create Date: 2025-09-11 18:20:59.628501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f77e2b58692'
down_revision: Union[str, Sequence[str], None] = '81431b1ca867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create languages table
    op.create_table('languages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('language_name', sa.String(100), nullable=False),
        sa.Column('language_code', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('language_name')
    )

    # Create index for better performance
    op.create_index('idx_languages_name', 'languages', ['language_name'])

    # Insert some common languages
    op.execute("""
        INSERT INTO languages (language_name, language_code) VALUES
        ('English', 'en'),
        ('Spanish', 'es'),
        ('French', 'fr'),
        ('German', 'de'),
        ('Italian', 'it'),
        ('Portuguese', 'pt'),
        ('Chinese', 'zh'),
        ('Japanese', 'ja'),
        ('Korean', 'ko'),
        ('Arabic', 'ar'),
        ('Hindi', 'hi'),
        ('Russian', 'ru'),
        ('Dutch', 'nl'),
        ('Swedish', 'sv'),
        ('Norwegian', 'no'),
        ('Danish', 'da'),
        ('Finnish', 'fi'),
        ('Polish', 'pl'),
        ('Czech', 'cs'),
        ('Hungarian', 'hu'),
        ('Greek', 'el'),
        ('Turkish', 'tr'),
        ('Hebrew', 'he'),
        ('Thai', 'th'),
        ('Vietnamese', 'vi'),
        ('Indonesian', 'id'),
        ('Malay', 'ms'),
        ('Filipino', 'fil'),
        ('Tagalog', 'tl')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the languages table
    op.drop_index('idx_languages_name', table_name='languages')
    op.drop_table('languages')

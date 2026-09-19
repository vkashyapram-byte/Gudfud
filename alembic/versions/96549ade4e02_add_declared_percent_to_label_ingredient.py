"""Add declared_percent to label_ingredient

Revision ID: 96549ade4e02
Revises: e5dfe0825277
Create Date: 2026-09-19 20:35:25.939973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96549ade4e02'
down_revision: Union[str, Sequence[str], None] = 'e5dfe0825277'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('label_ingredient', sa.Column('declared_percent', sa.Numeric(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('label_ingredient', 'declared_percent')

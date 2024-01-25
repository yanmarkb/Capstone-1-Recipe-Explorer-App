"""Add id column to favorites

Revision ID: fcb7c842aa65
Revises: 49f4bf17014a
Create Date: 2024-01-24 13:20:49.311552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcb7c842aa65'
down_revision: Union[str, None] = '49f4bf17014a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('favorites', sa.Column('id', sa.Integer, primary_key=True))

def downgrade():
    op.drop_column('favorites', 'id')

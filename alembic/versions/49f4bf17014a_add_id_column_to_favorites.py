"""Add id column to favorites

Revision ID: 49f4bf17014a
Revises: e0af018b8e6c
Create Date: 2024-01-24 13:20:37.646733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49f4bf17014a'
down_revision: Union[str, None] = 'e0af018b8e6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

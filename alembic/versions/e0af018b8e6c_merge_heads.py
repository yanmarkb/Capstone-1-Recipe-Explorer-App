"""merge heads

Revision ID: e0af018b8e6c
Revises: c210937b3840, d2cd9772a240
Create Date: 2024-01-24 13:20:18.498974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0af018b8e6c'
down_revision: Union[str, None] = ('c210937b3840', 'd2cd9772a240')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""merge heads

Revision ID: 372307d21f8f
Revises: f11797367677
Create Date: 2024-01-24 13:26:26.924456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372307d21f8f'
down_revision: Union[str, None] = 'f11797367677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

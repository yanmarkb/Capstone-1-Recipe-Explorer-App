"""merge heads

Revision ID: f11797367677
Revises: fcb7c842aa65
Create Date: 2024-01-24 13:24:44.716376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f11797367677'
down_revision: Union[str, None] = 'fcb7c842aa65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

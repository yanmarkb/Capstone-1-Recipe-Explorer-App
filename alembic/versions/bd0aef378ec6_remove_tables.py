"""remove tables

Revision ID: bd0aef378ec6
Revises: 4d47b6733b27
Create Date: 2024-02-09 08:05:16.047541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd0aef378ec6'
down_revision: Union[str, None] = '4d47b6733b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

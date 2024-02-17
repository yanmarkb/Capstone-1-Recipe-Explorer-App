"""Modified recipe table

Revision ID: 191ffe4a89ec
Revises: a34bc48ec38d
Create Date: 2024-02-16 19:00:13.301304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '191ffe4a89ec'
down_revision: Union[str, None] = 'a34bc48ec38d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

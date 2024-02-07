"""remove tables

Revision ID: 247ba6ee10d7
Revises: 372307d21f8f
Create Date: 2024-02-07 13:25:44.527866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '247ba6ee10d7'
down_revision: Union[str, None] = '372307d21f8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_table('user_recipes')
    op.drop_table('saved_recipes')


def downgrade() -> None:
    pass

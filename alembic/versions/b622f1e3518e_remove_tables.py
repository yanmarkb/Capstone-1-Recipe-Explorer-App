"""remove tables

Revision ID: b622f1e3518e
Revises: 247ba6ee10d7
Create Date: 2024-02-07 16:39:23.643708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b622f1e3518e'
down_revision: Union[str, None] = '247ba6ee10d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_table('user_recipes')
    op.drop_table('saved_recipes')


def downgrade() -> None:
    pass

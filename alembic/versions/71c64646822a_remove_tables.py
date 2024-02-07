"""remove tables

Revision ID: 71c64646822a
Revises: b622f1e3518e
Create Date: 2024-02-07 17:12:52.159634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71c64646822a'
down_revision: Union[str, None] = 'b622f1e3518e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_table('user_recipes')
    op.drop_table('saved_recipes')


def downgrade() -> None:
    pass

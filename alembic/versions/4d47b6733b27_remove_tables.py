"""remove tables

Revision ID: 4d47b6733b27
Revises: 71c64646822a
Create Date: 2024-02-09 07:55:33.562676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d47b6733b27'
down_revision: Union[str, None] = '71c64646822a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('ingredients')
    op.drop_table('recipe_ingredients')
    op.drop_table('user_recipes')
    op.drop_table('saved_recipes')


def downgrade() -> None:
    pass

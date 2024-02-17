"""Remove tables and modify recipes id

Revision ID: 7185e37fb94e
Revises: bd0aef378ec6
Create Date: 2024-02-16 18:37:13.083525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7185e37fb94e'
down_revision: Union[str, None] = 'bd0aef378ec6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('favorites_recipe_id_fkey', 'favorites', type_='foreignkey')
    op.alter_column('favorites', 'recipe_id', existing_type=sa.Integer(), type_=sa.String())
    op.execute('DROP TABLE IF EXISTS recipe_ingredients CASCADE')
    op.execute('DROP TABLE IF EXISTS ingredients CASCADE')
    op.execute('DROP TABLE IF EXISTS user_recipes CASCADE')
    op.execute('DROP TABLE IF EXISTS saved_recipes CASCADE')
    op.alter_column('recipes', 'id', existing_type=sa.Integer(), type_=sa.String(), autoincrement=False)
    op.create_foreign_key('favorites_recipe_id_fkey', 'favorites', 'recipes', ['recipe_id'], ['id'])


def downgrade():
    op.alter_column('recipes', 'id', existing_type=sa.String(), type_=sa.Integer())

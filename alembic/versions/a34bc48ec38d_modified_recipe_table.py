"""Modified recipe table

Revision ID: a34bc48ec38d
Revises: 7185e37fb94e
Create Date: 2024-02-16 18:51:24.282396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a34bc48ec38d'
down_revision: Union[str, None] = '7185e37fb94e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    
    if not 'recipe_id' in sa.Table('recipes', sa.MetaData()).columns:
        op.add_column('recipes', sa.Column('recipe_id', sa.Integer()))

    op.alter_column('recipes', 'recipe_id', existing_type=sa.Integer(), type_=sa.String())

def downgrade() -> None:
    pass

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData
from typing import Union, Sequence

# revision identifiers, used by Alembic.
revision: str = 'd2cd9772a240'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def table_exists(table_name: str) -> bool:
    metadata = MetaData()
    metadata.reflect(bind=op.get_bind())
    return table_name in metadata.tables

def upgrade():
    if not table_exists('favorites'):
        op.create_table(
            'favorites',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),  
            sa.Column('recipe_id', sa.Integer, sa.ForeignKey('recipes.id')),
            sa.UniqueConstraint('user_id', 'recipe_id', name='user_recipe_uc')
        )

def downgrade():
    if table_exists('favorites'):
        op.drop_table('favorites')
"""Modified recipe table

Revision ID: eae9510f8d82
Revises: 191ffe4a89ec
Create Date: 2024-02-16 20:42:00.583065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eae9510f8d82'
down_revision: Union[str, None] = '191ffe4a89ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('ALTER TABLE recipes ALTER COLUMN recipe_id TYPE INTEGER USING (recipe_id::integer)')


def downgrade():
    op.execute('ALTER TABLE recipes ALTER COLUMN recipe_id TYPE VARCHAR(255) USING (recipe_id::varchar)')

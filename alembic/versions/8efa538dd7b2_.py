"""empty message

Revision ID: 8efa538dd7b2
Revises: 38fc217c4b55
Create Date: 2024-01-23 14:47:41.962649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8efa538dd7b2'
down_revision = '38fc217c4b55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorites', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###

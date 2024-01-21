"""empty message

Revision ID: 6ce42c0cd817
Revises: 
Create Date: 2024-01-21 13:54:09.365292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ce42c0cd817'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(20), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(60), nullable=False)
    )

    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('main_ingredient', sa.String(100), nullable=False),
        sa.Column('additional_ingredients', sa.String(300), nullable=True),
        sa.Column('instructions', sa.Text, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    )

    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False)
    )

    op.create_table(
        'recipe_ingredients',
        sa.Column('recipe_id', sa.Integer, sa.ForeignKey('recipes.id'), primary_key=True),
        sa.Column('ingredient_id', sa.Integer, sa.ForeignKey('ingredients.id'), primary_key=True),
        sa.Column('quantity', sa.String(100), nullable=False)
    )

    op.create_table(
        'user_recipes',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('recipe_id', sa.Integer, sa.ForeignKey('recipes.id'), primary_key=True)
    )

    op.create_table(
        'saved_recipes',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('recipe_id', sa.Integer, sa.ForeignKey('recipes.id'), primary_key=True)
    )


def downgrade():
    op.drop_table('saved_recipes')
    op.drop_table('user_recipes')
    op.drop_table('recipe_ingredients')
    op.drop_table('ingredients')
    op.drop_table('recipes')
    op.drop_table('users')
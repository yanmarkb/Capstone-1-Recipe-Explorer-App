from models import db, connect_db, User, Recipe, Ingredient, RecipeIngredient, UserRecipe, SavedRecipe, Favorite
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///TheMealDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
connect_db(app)

db.drop_all()

db.create_all()
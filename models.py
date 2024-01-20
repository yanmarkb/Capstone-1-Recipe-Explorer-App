
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import session
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Bcrypt extension for hashing passwords.
bcrypt = Bcrypt()

# Initialize the SQLAlchemy extension for interacting with the database.
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def signup(cls, username, email, password, image_url):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    @property
    def password(self):
        """Password property."""
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        """Set password property."""
        self.password_hash = generate_password_hash(password)

    def veryify_password(self, password):
        """Check if password is correct."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def logout(cls):
        session.clear()

class Recipe(db.Model):
    """Recipe in the system."""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    main_ingredient = db.Column(db.String(100), nullable=False)
    additional_ingredients = db.Column(db.String(300), nullable=True)
    instructions = db.Column(db.Text, nullable=False)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True)

class Ingredient(db.Model):
    """Ingredient in the system."""
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('RecipeIngredient', backref='ingredient', lazy=True)

class RecipeIngredient(db.Model):
    """RecipeIngredient in the system."""
    __tablename__ = 'recipe_ingredients'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    quantity = db.Column(db.String(100), nullable=False)

class UserRecipe(db.Model):

    __tablename__ = 'user_recipes'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)

class SavedRecipe(db.Model):

    __tablename__ = 'saved_recipes'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)

def connect_db(app):
    """Connect this database to provided Flask app.
    """

    # Set the app attribute of the db object to the provided Flask app.
    db.app = app

    # Call the init_app method of the db object to complete the connection.
    db.init_app(app)

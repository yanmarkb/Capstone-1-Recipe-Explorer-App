from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import session
from flask import current_app as app
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Initialize the SQLAlchemy extension for interacting with the database.
db = SQLAlchemy()

# class User(db.Model):
#     """User in the system."""
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(60), nullable=False)
#     recipes = db.relationship('Recipe', backref='author', lazy=True)

#     def check_password(self, password):
#         return bcrypt.check_password_hash(self.password_hash, password)

#     @classmethod
#     def signup(cls, username, email, password, image_url):
#         hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

#         user = User(
#             username=username,
#             email=email,
#             password_hash=hashed_pwd,
#             image_url=image_url,
#         )

#         db.session.add(user)
#         db.session.commit()  
#         return user

#     @classmethod
#     def authenticate(cls, username, password):
#         user = cls.query.filter_by(username=username).first()

#         if user:
#             is_auth = bcrypt.check_password_hash(user.password_hash, password)
#             if is_auth:
#                 return user

#         return False

#     @property
#     def password(self):
#         """Password property."""
#         raise AttributeError('Password is not a readable attribute.')

#     @password.setter
#     def password(self, password):
#         """Set password property."""
#         self.password_hash = generate_password_hash(password)

#     def verify_password(self, password):
#         """Check if password is correct."""
#         return check_password_hash(self.password_hash, password)

#     @classmethod
#     def logout(cls):
#         session.clear()

class User(db.Model):
    """User in the system."""

    # Set the name of the table in the database.
    __tablename__ = 'users'

    # Define a column for the ID of the user, which is the primary key for the users table.
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # Define a column for the email of the user, which is required and must be unique.
    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    # Define a column for the username of the user, which is required and must be unique.
    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    # Define a column for the image URL of the user, which defaults to a placeholder image.
    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    # Define a column for the header image URL of the user, which defaults to a placeholder image.
    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    # Define a column for the bio of the user, which is optional.
    bio = db.Column(
        db.Text,
    )

    # Define a column for the location of the user, which is optional.
    location = db.Column(
        db.Text,
    )

    # Define a column for the password of the user, which is required.
    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def check_password(self, password):
        """Check password against hashed version."""
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

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
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    @classmethod
    def logout(cls):
            """Clear the session to log out the user."""
            session.clear()  # Clear the session to log out the user.


class Recipe(db.Model):
    """Recipe in the system."""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    main_ingredient = db.Column(db.String(100), nullable=False)
    additional_ingredients = db.Column(db.String(300), nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.String(100), nullable=False)

class UserRecipe(db.Model):
    __tablename__ = 'user_recipes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)

class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)

def connect_db(app):
    """Connect this database to provided Flask app."""
    db.app = app
    db.init_app(app)
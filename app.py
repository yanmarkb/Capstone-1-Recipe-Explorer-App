import os
from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from forms import LoginForm, RegistrationForm
from models import connect_db, db, User, Recipe, Ingredient, RecipeIngredient, UserRecipe, SavedRecipe
from flask_migrate import Migrate

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///TheMealDB'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
toolbar = DebugToolbarExtension(app)
connect_db(app)

from models import User, Recipe, Ingredient, RecipeIngredient, UserRecipe, SavedRecipe

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.before_request
def add_user_to_g():
    """If a user is logged in, add the current user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.route('/', methods=['GET', 'POST'])
def home():
    if g.user is None:
        return redirect(url_for('login'))

    meals = []
    if request.method == 'POST':
        main_ingredient = request.form.get('main_ingredient')
        extra_ingredients = request.form.get('extra_ingredients').split(',')

        response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={main_ingredient}')
        meals = response.json().get('meals', [])

        for ingredient in extra_ingredients:
            response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}')
            meals += response.json().get('meals', [])

    return render_template('index.html', meals=meals)

@app.route('/meal/<id>')
@login_required
def meal(id):
    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}')
    meal = response.json().get('meals', [])[0]
    return render_template('meal.html', meal=meal)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            session[CURR_USER_KEY] = user.id
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            flash('Username or Email already exists', 'danger')
            db.session.rollback()
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session[CURR_USER_KEY] = user.id
            g.user = user
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    g.user = None
    flash("You have successfully logged out. See you later!", "success")
    return redirect('/')

@app.route('/users')
@login_required
def list_users():
    """Page with listing of users."""
    search = request.args.get('q')
    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    return render_template('users/index.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
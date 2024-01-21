import os
import requests
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb
from flask_migrate import Migrate
from models import connect_db, db, User, Recipe, Ingredient, RecipeIngredient, UserRecipe, SavedRecipe
from forms import LoginForm, RegistrationForm
from flask_bcrypt import Bcrypt
import random

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///TheMealDB"
app.config['SECRET_KEY'] = "it's a secret"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)
connect_db(app)
migrate = Migrate(app, db)

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///TheMealDB'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    migrate = Migrate(app, db)

    toolbar = DebugToolbarExtension(app)
    connect_db(app)

    bcrypt.init_app(app)

    return app

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

def do_login(user):
    """Log in a user."""
    session[CURR_USER_KEY] = user.id

def do_logout():    
    """Logout a user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/', methods=['GET', 'POST'])
def home():
    if g.user is None:
        return redirect(url_for('login'))

    meals = session.pop('meals', [])  # get and remove the meals from session

    if request.method == 'POST':
        main_ingredient = request.form.get('main_ingredient')
        extra_ingredients = request.form.get('extra_ingredients').split(',')

        response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={main_ingredient}')
        meals = response.json().get('meals', [])

        for ingredient in extra_ingredients:
            response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}')
            meals += response.json().get('meals', [])

    # Select 3 random meals if there are more than 3 meals
    if len(meals) > 3:
        meals = random.sample(meals, 3)

    return render_template('index.html', meals=meals)

    return render_template('index.html', meals=meals)

@app.route('/meal/<id>', methods=['GET', 'POST'])
@login_required
def meal(id):
    if request.method == 'POST':
        search_query = request.form.get('search')
        response = requests.get(f'https://www.themealdb.com/api/json/v1/1/search.php?s={search_query}')
        meals = response.json().get('meals', [])
        if meals:
            session['meals'] = meals 
            return redirect(url_for('home'))

    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}')
    meal = response.json().get('meals', [])[0]
    return render_template('meal.html', meal=meal)

@app.route('/search', methods=['POST'])
@login_required
def search():
    main_ingredient = request.form.get('main_ingredient')
    extra_ingredients = request.form.get('extra_ingredients').split(',')

    # Get meals with the main ingredient
    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={main_ingredient}')
    meals = response.json().get('meals', [])

    # Filter meals that contain all extra ingredients
    for ingredient in extra_ingredients:
        response = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient.strip()}')
        ingredient_meals = response.json().get('meals', [])
        meals = [meal for meal in meals if meal in ingredient_meals]

    if meals:
        session['meals'] = meals  # store the meals in session
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user signup."""
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)
        do_login(user)
        return redirect("/")
    else:
        return render_template('register.html', form=form)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(email=form.email.data).first()
    #     if user and bcrypt.check_password_hash(user.password, form.password.data):
    #         session[CURR_USER_KEY] = user.id
    #         g.user = user
    #         return redirect(url_for('home'))
    #     else:
    #         flash('Login Unsuccessful. Please check email and password', 'danger')
    # return render_template('login.html', title='Login', form=form)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        flash("Invalid credentials.", 'danger')
    return render_template('login.html', form=form)

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
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app = create_app()
    db.create_all()
    app.run(debug=True)
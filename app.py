import os
import requests
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb
from flask_migrate import Migrate
from models import connect_db, db, User, Recipe, Ingredient, RecipeIngredient, UserRecipe, SavedRecipe, Favorite
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
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)
connect_db(app)
migrate = Migrate(app, db)

def create_app():
    app = Flask(__name__)
    bcrypt = Bcrypt(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///TheMealDB"
    app.config['SECRET_KEY'] = "it's a secret"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    toolbar = DebugToolbarExtension(app)
    connect_db(app)
    migrate = Migrate(app, db)

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


@app.route('/', methods=['GET', 'POST'])
def home():
    
    if g.user is None:
        return redirect(url_for('login'))

    meals = session.pop('meals', []) 

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

    return render_template('index.html', meals=meals, meal=meal)

@app.route('/meal/<id>', methods=['GET', 'POST'])
@login_required
def meal(id):
    if request.method == 'POST':
        favorite = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first()
        if favorite:
            db.session.delete(favorite)
        else:
            favorite = Favorite(user_id=g.user.id, recipe_id=id)
            db.session.add(favorite)
        db.session.commit()
        return redirect(url_for('show_favorites', user_id=g.user.id))

    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}')
    meal = response.json().get('meals', [])[0]
    meal['id'] = meal['idMeal']
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
        session['meals'] = meals 
    return redirect(url_for('home'))

def add_favorite(user_id, recipe_id):
    """Add a recipe to a user's favorites."""

    
    favorite = Favorite(user_id=user_id, recipe_id=recipe_id)

   
    db.session.add(favorite)
    db.session.commit()

@app.route('/meal/toggle_favorite/<int:meal_id>', methods=['POST'])
@login_required
def toggle_favorite(meal_id):
    """Toggle a favorited meal for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    meal = Recipe.query.get_or_404(meal_id)

    favorite = Favorite.query.filter_by(user_id=g.user.id, recipe_id=meal.id).first()

    if favorite:
        # If the user has already favorited the meal, remove the favorite
        db.session.delete(favorite)
    else:
        # If the user hasn't favorited the meal, add a new favorite
        add_favorite(g.user.id, meal.id)

    db.session.commit()

    # Redirect to the referrer URL if it's set, otherwise redirect to the home page
    return redirect(request.referrer or url_for('index'))


@app.route('/users/<int:user_id>/favorites', methods=['GET', 'POST'])
@login_required
def show_favorites(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        if recipe_id is None:
            flash('Recipe ID is missing.', 'error')
            return redirect(url_for('show_favorites', user_id=user.id))
        recipe_id = int(recipe_id)
        recipe = Recipe.query.get(recipe_id)
        if recipe is None:
            response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_id}')
            if response.status_code == 200:
                meal = response.json().get('meals', [])[0]
                recipe = Recipe(id=recipe_id, title=meal['strMeal'])
                db.session.add(recipe)
            else:
                flash('Recipe not found in TheMealDB API.', 'error')
                return redirect(url_for('show_favorites', user_id=user.id))
        favorite = Favorite(user_id=user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Recipe added to favorites.', 'success')
        return redirect(url_for('show_favorites', user_id=user.id))

    else: 
        favorites = Favorite.query.filter_by(user_id=user.id).all()
        meals = [favorite.recipe for favorite in favorites]
        meal = [favorite.recipe for favorite in favorites]
        return render_template('show_favorites.html', user=user, favorites=favorites, meals=meals, meal=meal)
        
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

@app.route('/users/<int:user_id>')
@login_required
def users_show(user_id):
    """Show user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/", 403)
    user = User.query.get_or_404(user_id)
    recipes = (Recipe
                .query
                .filter(Recipe.user_id == user_id)
                .order_by(Recipe.created_at.desc())
                .all())
    return render_template('users/show.html', user=user, recipes=recipes)

if __name__ == '__main__':
    app = create_app()
    db.create_all()
    app.run(debug=True)
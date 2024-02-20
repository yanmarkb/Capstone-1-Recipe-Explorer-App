import os
import requests
import random
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import pdb
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import connect_db, db, migrate, User, Recipe, Favorite
from forms import LoginForm, RegistrationForm
from flask_bcrypt import Bcrypt
import random
from concurrent.futures import ThreadPoolExecutor

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///TheMealDB"
app.config['SECRET_KEY'] = "it's a secret"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.init_app(app)
migrate.init_app(app, db)
toolbar = DebugToolbarExtension(app)
connect_db(app)
# migrate = Migrate(app, db)

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
                bio=form.bio.data,
                location=form.location.data
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

    # Check if the meal is favorited by the current user
    is_favorited = Favorite.query.filter_by(user_id=g.user.id, recipe_id=id).first() is not None

    return render_template('meal.html', meal=meal, is_favorited=is_favorited)

def search_meals(main_ingredient, extra_ingredients):
    # Send requests to the APIs
    filter_url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={main_ingredient}"
    search_main_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={main_ingredient}"
    filter_response = requests.get(filter_url).json()
    search_main_response = requests.get(search_main_url).json()

    # Get the meals from the responses
    filter_meals = filter_response.get('meals')
    search_main_meals = search_main_response.get('meals')

    # If the meals are None, replace them with an empty list
    if filter_meals is None:
        filter_meals = []
    if search_main_meals is None:
        search_main_meals = []

    # If there are no meals in both responses, return an empty list
    if not filter_meals and not search_main_meals:
        return []

    # Combine meals from both responses
    all_meals = filter_meals + search_main_meals

    # If extra_ingredients is not empty, filter meals based on extra ingredients
    if extra_ingredients:
        def meal_passes_filter(meal):
            meal_id = meal['idMeal']
            lookup_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
            lookup_response = requests.get(lookup_url).json()
            lookup_meal = lookup_response.get('meals', [])[0]
            lookup_ingredients = set(lookup_meal.values())
            return all(ingredient in lookup_ingredients for ingredient in extra_ingredients)

        with ThreadPoolExecutor() as executor:
            meal_results = executor.map(meal_passes_filter, all_meals)
            all_meals = [meal for meal, passes in zip(all_meals, meal_results) if passes]

    # Remove duplicates
    unique_meals = list({meal['idMeal']: meal for meal in all_meals}.values())

    # If there are more than 3 meals, select 3 random ones
    if len(unique_meals) > 3:
        unique_meals = random.sample(unique_meals, 3)

    return unique_meals

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        main_ingredient = request.form.get('main_ingredient')
        extra_ingredients = request.form.get('extra_ingredients').split(',')
        meals = search_meals(main_ingredient, extra_ingredients)

        for meal in meals:
            if 'strInstructions' not in meal:
                flash("There are no meals with this ingredient/ingredients, please use a different term")
                return redirect(url_for('home')) 

            recipe = Recipe.query.filter_by(title=meal['strMeal']).first()
            if not recipe:
                recipe = Recipe(
                    title=meal['strMeal'],
                    main_ingredient=main_ingredient,
                    additional_ingredients=','.join(extra_ingredients),
                    instructions=meal['strInstructions'], 
                    user_id=g.user.id,
                    recipe_id=meal['idMeal']
                )
                db.session.add(recipe)
        db.session.commit()

        return render_template('index.html', meals=meals)
    return render_template('index.html')

def add_favorite(user_id, recipe_id):
    """Add a recipe to a user's favorites."""
    
    favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if favorite is None:
        favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()

@app.route('/meal/toggle_favorite/<int:meal_id>', methods=['POST'])
@login_required
def toggle_favorite(meal_id):
    """Toggle a favorited meal for the currently-logged-in user."""

    # Convert meal_id to string
    meal_id_str = str(meal_id)

    # Check if the recipe exists
    recipe = Recipe.query.get(meal_id_str)
    if recipe is None:
        # If the recipe doesn't exist, fetch it from API
        response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}')
        meal_data = response.json().get('meals', [])[0]

        # Create a new recipe
        recipe = Recipe(
            id=meal_id_str, 
            title=meal_data['strMeal'], 
            main_ingredient=meal_data['strIngredient1'], 
            additional_ingredients=','.join([meal_data[f'strIngredient{i}'] for i in range(2, 21) if meal_data[f'strIngredient{i}']]), 
            instructions=meal_data['strInstructions'], 
            user_id=g.user.id
        )
        db.session.add(recipe)
        db.session.commit()

    favorite = Favorite.query.filter_by(user_id=str(g.user.id), recipe_id=meal_id_str).first()

    if favorite:
        # If the user has already favorited the meal, remove the favorite
        db.session.delete(favorite)
    else:
        # If the user hasn't favorited the meal, add a new favorite
        add_favorite(str(g.user.id), meal_id_str)

    db.session.commit()

    # Check if the meal is now favorited by the current user
    is_favorited = Favorite.query.filter_by(user_id=str(g.user.id), recipe_id=meal_id_str).first() is not None

    return jsonify({'isFavorited': is_favorited})

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
        add_favorite(user.id, recipe_id)
        flash('Recipe added to favorites.', 'success')
        return redirect(url_for('show_favorites', user_id=user.id))

    else: 
        favorites = Favorite.query.filter_by(user_id=user.id).all()
        meals = [favorite.recipe for favorite in favorites]
        return render_template('show_favorites.html', user=user, favorites=favorites, meals=meals)

@app.route('/meal/is_favorited/<int:meal_id>', methods=['GET'])
@login_required
def is_favorited(meal_id):
    favorite = Favorite.query.filter_by(user_id=g.user.id, recipe_id=meal_id).first()
    is_favorited = favorite is not None
    return jsonify({'isFavorited': is_favorited})
        
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
                .all())
    form = RegistrationForm(obj=user)  # Create form with user data
    return render_template('users/show.html', user=user, recipes=recipes, form=form)

@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(g.user.id)
    form = RegistrationForm(obj=user)
    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or user.image_url
            user.bio = form.bio.data
            user.location = form.location.data
            db.session.commit()
            return redirect(f"/users/{user.id}")
        else:
            flash("Invalid password, please try again.", "danger")
    return render_template("users/edit.html", form=form, user=user)

if __name__ == '__main__':
    app.run(debug=True)
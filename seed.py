import requests
from models import Recipe
from app import db

# Send a GET request to the API to get all meal IDs
response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=')
meal_ids = [meal['idMeal'] for meal in response.json()['meals']]

# Loop through each meal ID
for meal_id in meal_ids:
    # Get the meal details
    response = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}')
    meal = response.json()['meals'][0]

    # Create a new Recipe object with the data from the API
    recipe = Recipe(
        title=meal['strMeal'],
        main_ingredient=meal['strIngredient1'],
        additional_ingredients=meal['strIngredient2'],
        instructions=meal['strInstructions'],
    )

    # Add the new recipe to the session
    db.session.add(recipe)

# Commit the session to save the changes
db.session.commit()
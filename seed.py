import requests
from models import Recipe
from app import db

# Send a GET request to the API
response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=Arrabiata')

# Parse the data into a Python dictionary
data = response.json()

# Loop through the meals in the data
for meal in data['meals']:
    # Create a new Recipe object with the data from the API
    recipe = Recipe(
        title=meal['strMeal'],
        main_ingredient=meal['strIngredient1'],
        additional_ingredients=meal['strIngredient2'],
        instructions=meal['strInstructions'],
        user_id=1  # Replace this with the actual user ID
    )

    # Add the new recipe to the session
    db.session.add(recipe)

# Commit the session to save the changes
db.session.commit()
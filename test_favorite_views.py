import os
import sys
import unittest

from models import db, User, Recipe, Favorite
from app import app, CURR_USER_KEY
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///TheMealDB"

class FavoriteViewTestCase(unittest.TestCase):
    """Test views for favorites."""

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['DEBUG'] = False
        with self.app.app_context():
            self.session = db.session
            existing_user = User.query.filter_by(email="test@test.com").first()
            if existing_user:
                self.session.delete(existing_user)
                self.session.commit()

            self.user = User.signup(username="testuser", email="test@test.com", password="password", image_url=None, bio=None, location=None)
            self.session.add(self.user)
            self.session.commit() 

            self.user_id = self.user.id

            existing_recipe = Recipe.query.get(1)
            if existing_recipe:
                self.session.delete(existing_recipe)
                self.session.commit()

            self.recipe = Recipe(id=1, title="Test Recipe")
            self.session.add(self.recipe)
            self.session.commit()

            self.recipe_id = self.recipe.id 


    def tearDown(self):
        with app.app_context():
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value is not None:
                db.session.rollback()
            else:
                db.session.commit()

    def test_search(self):
        with self.client.session_transaction() as session:
            with self.app.app_context():
                self.user = User.query.get(self.user_id)
                session[CURR_USER_KEY] = self.user.id 

        response = self.client.post('/search', data={'main_ingredient': 'chicken', 'extra_ingredients': 'onion,garlic'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_toggle_favorite(self):
        with self.client.session_transaction() as session:
            with self.app.app_context():
                self.user = User.query.get(self.user_id)
                session[CURR_USER_KEY] = self.user.id 

        response = self.client.post(f'/meal/toggle_favorite/{self.recipe.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            favorite = Favorite.query.filter_by(user_id=self.user.id, recipe_id=self.recipe.id).first()
            self.assertIsNotNone(favorite)

        response = self.client.post(f'/meal/toggle_favorite/{self.recipe.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            favorite = Favorite.query.filter_by(user_id=self.user.id, recipe_id=self.recipe.id).first()
            self.assertIsNone(favorite)
            

if __name__ == "__main__":
    unittest.main()
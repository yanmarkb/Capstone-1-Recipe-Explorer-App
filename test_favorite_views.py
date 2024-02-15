import os
import sys
import unittest

from models import db, User, Recipe, Favorite
from app import app
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///TheMealDB"

class FavoriteViewTestCase(unittest.TestCase):
    """Test views for favorites."""

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        with self.app.app_context():
            existing_user = User.query.filter_by(email="test@test.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()

            self.user = User.signup(username="testuser", email="test@test.com", password="password", image_url=None, bio=None, location=None)
            db.session.add(self.user)
            db.session.commit() 

            self.user_id = self.user.id

            existing_recipe = Recipe.query.get(1)
            if existing_recipe:
                db.session.delete(existing_recipe)
                db.session.commit()

            self.recipe = Recipe(id=1, title="Test Recipe")
            db.session.add(self.recipe)
            db.session.commit()

            self.recipe_id = self.recipe.id 

    def tearDown(self):
        with app.app_context():
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value is not None:
                db.session.rollback()
            else:
                db.session.commit()

    def test_toggle_favorite(self):
        with self.app.app_context():
            user = User.query.get(self.user_id)

            with self.client.session_transaction() as session:
                session['user_id'] = user.id

            response = self.client.post('/meal/toggle_favorite/1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            favorite = Favorite.query.filter_by(user_id=user.id, recipe_id=self.recipe_id).first()
            print(f"Favorite after first post: {favorite}") 
            self.assertIsNotNone(favorite)

            response = self.client.post('/meal/toggle_favorite/1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            favorite = Favorite.query.filter_by(user_id=user.id, recipe_id=self.recipe_id).first()
            print(f"Favorite after second post: {favorite}")  
            self.assertIsNone(favorite)
            

if __name__ == "__main__":
    unittest.main()
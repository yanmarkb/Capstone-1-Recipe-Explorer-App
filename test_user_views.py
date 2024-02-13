import os
import sys
import unittest
from models import db, User, Recipe, Favorite
from app import app
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///Test_TheMealDB"

class UserModelTestCase(unittest.TestCase):
    """Test views for messages."""

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

            # Define self.recipe
            existing_recipe = Recipe.query.get(1)
            if existing_recipe:
                db.session.delete(existing_recipe)
                db.session.commit()

            self.recipe = Recipe(id=1, title="Test Recipe")
            db.session.add(self.recipe)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value is not None:
                db.session.rollback()
            else:
                db.session.commit()

    def test_toggle_favorite(self):
        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    db.session.begin_nested()
                    sess['user_id'] = self.user.id

            response = c.post(f'/meal/toggle_favorite/{self.recipe.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            favorite = Favorite.query.filter_by(user_id=self.user.id, recipe_id=self.recipe.id).first()
            self.assertIsNotNone(favorite)

            response = c.post(f'/meal/toggle_favorite/{self.recipe.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            favorite = Favorite.query.filter_by(user_id=self.user.id, recipe_id=self.recipe.id).first()
            self.assertIsNone(favorite)

            db.session.rollback()

    def test_show_favorites(self):
        with self.app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    # Use the stored user id to get the user
                    user = User.query.get(self.user_id)
                    sess['user_id'] = user.id

                response = c.get(f'/users/{user.id}/favorites', follow_redirects=True)
                self.assertEqual(response.status_code, 200)

    def test_is_favorited(self):
        with app.app_context():
            db.session.add(self.user)
            db.session.add(self.recipe)
            db.session.commit()

            # Create a Favorite object for the test user and recipe
            favorite = Favorite(user_id=self.user.id, recipe_id=self.recipe.id)
            db.session.add(favorite)
            db.session.commit()

            with self.client as c:
                with c.session_transaction() as sess:
                    sess['user_id'] = self.user.id

                response = c.get(f'/meal/is_favorited/{self.recipe.id}', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {'isFavorited': True})

if __name__ == "__main__":
    unittest.main()
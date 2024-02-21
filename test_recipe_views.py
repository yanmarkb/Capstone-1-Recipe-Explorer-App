import os
import sys
import unittest

from models import db, User, Recipe, Favorite
from app import app, CURR_USER_KEY
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///TheMealDB"

class RecipeViewTestCase(unittest.TestCase):
    """Test views for recipes."""

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

    def tearDown(self):
        with app.app_context():
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value is not None:
                db.session.rollback()
            else:
                db.session.commit()

    def test_show_favorites(self):
        """Can a user view their favorites?"""

        with self.app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
    
                    user = User.query.get(self.user_id)
                    sess['user_id'] = user.id

                response = c.get(f'/users/{user.id}/favorites', follow_redirects=True)
                self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()


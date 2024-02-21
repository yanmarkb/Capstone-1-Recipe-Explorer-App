import os
import sys
import unittest
import time
from models import db, User, Recipe, Favorite
from app import app, CURR_USER_KEY
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
                
    def test_search(self):
        with self.client.session_transaction() as session:
            with self.app.app_context():
                self.user = User.query.get(self.user_id)
                session[CURR_USER_KEY] = self.user.id 

        response = self.client.post('/search', data={'main_ingredient': 'chicken', 'extra_ingredients': 'onion,garlic'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        """Can user register successfully?"""
        with self.client as c:
            data = {"username": "newuser", "email": "new@test.com", "password": "newpassword"}
            response = c.post("/register", data=data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("newuser", response.get_data(as_text=True))

    def test_user_login(self):
        """Can user login successfully?"""
        with self.client as c:
            data = {"username": "testuser", "password": "password"}
            response = c.post("/login", data=data, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("testuser", response.get_data(as_text=True))

    def test_user_logout(self):
        """Can user logout successfully?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = c.get("/logout", follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertNotIn("testuser", response.get_data(as_text=True))

    def test_user_profile_page(self):
        """Can user view their profile page?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            response = c.get(f"/users/{self.user_id}")

            self.assertEqual(response.status_code, 302)
            print(response.location) 



if __name__ == "__main__":
    unittest.main()
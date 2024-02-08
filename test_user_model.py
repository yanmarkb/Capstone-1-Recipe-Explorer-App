import os
from unittest import TestCase
from models import db, User
from app import app
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///Test_TheMealDB"

class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all() 
        db.create_all()

        User.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1", email="test1@test.com", password="testpassword", image_url=None, bio=None, location=None)
        self.testuser2 = User.signup(username="testuser2", email="test2@test.com", password="testpassword", image_url=None, bio=None, location=None)
        db.session.commit()

    def tearDown(self):
        """Rollback problems that occurred during tests."""

        db.session.rollback()
        self.app_context.pop()

    def test_repr(self):
        """Does the repr method work as expected?"""
        with self.app_context:
            self.assertEqual(repr(self.testuser1), f"<User #{self.testuser1.id}: {self.testuser1.username}, {self.testuser1.email}>")

    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        with self.app_context:
            user = User.signup("testuser3", "test3@test.com", "testpassword", None, None, None)
            db.session.commit()

            found_user = User.query.filter_by(username="testuser3").first()
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.email, "test3@test.com")

    def test_user_create_fail(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        with self.app_context:
            with self.assertRaises(IntegrityError):
                invalid_user = User.signup(None, "test4@test.com", "testpassword", None, None, None)
                db.session.commit()

    def test_user_authenticate_success(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        with self.app_context:
            user = User.authenticate(self.testuser1.username, "testpassword")
            self.assertIsNotNone(user)
            self.assertEqual(user.id, self.testuser1.id)

    def test_user_authenticate_fail_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with self.app_context:
            self.assertFalse(User.authenticate("invalidusername", "testpassword"))

    def test_user_authenticate_fail_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with self.app_context:
            self.assertFalse(User.authenticate(self.testuser1.username, "invalidpassword"))
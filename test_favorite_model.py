from models import db, User, Favorite, Recipe
from app import app
from sqlalchemy.exc import IntegrityError
import os
from unittest import TestCase

os.environ['DATABASE_URL'] = "postgresql:///Test_TheMealDB"

class FavoriteModelTestCase(TestCase):
    """Test views for favorites."""

    def setUp(self):
        """Create test client, add sample data."""

        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all() 
        db.create_all()

        User.query.delete()
        Favorite.query.delete()
        Recipe.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1", email="test1@test.com", password="testpassword", image_url=None, bio=None, location=None)
        db.session.commit()

        self.testrecipe1 = Recipe(id=1, title="Test Recipe")
        self.testrecipe2 = Recipe(id=2, title="Test Recipe 2")
        db.session.add_all([self.testrecipe1, self.testrecipe2])
        db.session.commit()

        self.testfavorite1 = Favorite(user_id=self.testuser1.id, recipe_id=self.testrecipe1.id)
        db.session.add(self.testfavorite1)
        db.session.commit()

    def tearDown(self):
        """Rollback problems that occurred during tests."""

        db.session.rollback()
        self.app_context.pop()

    def test_favorite_create(self):
        """Does Favorite.create successfully create a new favorite given valid user and recipe?"""
        with self.app_context:
            favorite = Favorite(user_id=self.testuser1.id, recipe_id=self.testrecipe2.id)
            db.session.add(favorite)
            db.session.commit()

            found_favorite = Favorite.query.filter_by(user_id=self.testuser1.id, recipe_id=self.testrecipe2.id).first()
            self.assertIsNotNone(found_favorite)


    def test_favorite_create_fail(self):
        """Does Favorite.create fail to create a new favorite if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        with self.app_context:
            # Try to create a duplicate favorite
            duplicate_favorite = Favorite(user_id=self.testuser1.id, recipe_id=self.testrecipe1.id)
            with self.assertRaises(IntegrityError):
                db.session.add(duplicate_favorite)
                db.session.commit()

    def test_favorite_create_no_user_id(self):
        """Does Favorite.create fail to create a new favorite if user_id is None?"""
        with self.app_context:
            invalid_favorite = Favorite(user_id=None, recipe_id=self.testrecipe1.id)
            db.session.add(invalid_favorite)
            print("Added invalid favorite to session")
            try:
                db.session.flush()
                print("Flushed session")
            except IntegrityError:
                print("Caught IntegrityError")
                raise

    def __repr__(self):
        return f"<Favorite #{self.id}: User {self.user_id} - Recipe {self.recipe_id}>"

    def test_favorite_create_with_valid_credentials(self):
        """Does Favorite.create successfully create a new favorite given valid user and recipe?"""
        with self.app_context:
            favorite = Favorite(user_id=self.testuser1.id, recipe_id=self.testrecipe2.id)
            db.session.add(favorite)
            db.session.commit()

            found_favorite = Favorite.query.filter_by(user_id=self.testuser1.id, recipe_id=self.testrecipe2.id).first()
            self.assertIsNotNone(found_favorite)

    def test_favorite_create_with_invalid_credentials(self):
        """Does Favorite.create fail to create a new favorite if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        with self.app_context:
            # Try to create a favorite with non-existent user and recipe
            invalid_favorite = Favorite(user_id=999, recipe_id=999)
            with self.assertRaises(IntegrityError):
                db.session.add(invalid_favorite)
                db.session.commit()

    def test_favorite_exists(self):
        """Does a favorite exist when given a valid user_id and recipe_id?"""
        with self.app_context:
            found_favorite = Favorite.query.filter_by(user_id=self.testuser1.id, recipe_id=self.testrecipe1.id).first()
            self.assertIsNotNone(found_favorite)
            self.assertEqual(found_favorite.user_id, self.testuser1.id)
            self.assertEqual(found_favorite.recipe_id, self.testrecipe1.id)
import os
from unittest import TestCase
from models import db, User, Recipe
from app import app

os.environ['DATABASE_URL'] = "postgresql:///recipe-test"

class RecipeModelTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.testuser = User.signup(username="testuser", email="test@test.com", password="testpassword", image_url=None, bio=None, location=None)
        db.session.commit()

        self.testrecipe = Recipe(title="testrecipe", main_ingredient="testingredient", additional_ingredients="testadditional", instructions="testinstructions", user_id=self.testuser.id)
        db.session.add(self.testrecipe)
        db.session.commit()

    def tearDown(self):
        """Rollback problems that occurred during tests."""

        db.session.rollback()
        self.app_context.pop()

    def test_recipe_model(self):
        """Does basic model work?"""

        r = Recipe.query.get(self.testrecipe.id)

        self.assertEqual(r.title, "testrecipe")
        self.assertEqual(r.main_ingredient, "testingredient")
        self.assertEqual(r.additional_ingredients, "testadditional")
        self.assertEqual(r.instructions, "testinstructions")
        self.assertEqual(r.user_id, self.testuser.id)
    
    def test_new_recipe(self):
        """Can we add a new recipe?"""

        r = Recipe(title="newrecipe", main_ingredient="newingredient", additional_ingredients="newadditional", instructions="newinstructions", user_id=self.testuser.id)
        db.session.add(r)
        db.session.commit()

        self.assertEqual(r.title, "newrecipe")
        self.assertEqual(r.main_ingredient, "newingredient")
        self.assertEqual(r.additional_ingredients, "newadditional")
        self.assertEqual(r.instructions, "newinstructions")
        self.assertEqual(r.user_id, self.testuser.id)

    def test_delete_recipe(self):
        """Can we delete a recipe?"""

        r = Recipe.query.get(self.testrecipe.id)
        db.session.delete(r)
        db.session.commit()

        r = Recipe.query.get(self.testrecipe.id)
        self.assertIsNone(r)

    def test_update_recipe(self):
        """Can we update a recipe?"""

        r = Recipe.query.get(self.testrecipe.id)
        r.title = "updatedrecipe"
        db.session.commit()

        r = Recipe.query.get(self.testrecipe.id)
        self.assertEqual(r.title, "updatedrecipe")

    def test_user_recipe_relationship(self):
        """Do the user and recipe models correctly relate to each other?"""

        u = User.query.get(self.testuser.id)
        self.assertEqual(len(u.recipes), 1)
        self.assertEqual(u.recipes[0].id, self.testrecipe.id)
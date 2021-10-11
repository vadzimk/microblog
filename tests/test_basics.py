# filename must begin with test_
import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        """ runs before each test """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """ runs after each test """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # name of test begins with test_
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])  # lowercase testing did not pass

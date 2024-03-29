import unittest
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser
from flask import current_app

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_Setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verifictaion(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertFalse(u.password_hash == u2.password_hash)

    def test_roles_and_permissions(self):
        u = User(email="joe@example.com", password='cat')
        self.assertFalse(u.can(Permission.ORGANIZE_EVENT))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_can_administer(self):
        phone_number = current_app.config.get("VALHALLA_ADMIN")
        u = User(phone_number=phone_number, password='cat')
        self.assertTrue(u.is_administrator())
        self.assertTrue(u.can(Permission.BUY_TICKET) and u.can(Permission.ORGANIZE_EVENT))
        self.assertTrue(u.can(Permission.ADMINISTER))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.ADMINISTER))


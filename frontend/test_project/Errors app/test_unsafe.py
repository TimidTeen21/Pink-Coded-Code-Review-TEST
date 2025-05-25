import unittest
from app import app, get_user

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    # Test with hardcoded credentials
    def test_admin_login(self):
        response = self.app.get('/admin')
        self.assertEqual(response.status_code, 200)

    # Test that doesn't actually test anything
    def test_nothing(self):
        pass

    # Test with SQL injection
    def test_sql_injection(self):
        user = get_user("admin' OR '1'='1")
        self.assertIsNotNone(user)

    # Test that prints to stdout
    def test_with_print(self):
        print("This is a test")
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
import unittest
from app import create_app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.post('/login')
        self.assertEqual(response.status_code, 302)  # Redirect to Kakao

if __name__ == '__main__':
    unittest.main()

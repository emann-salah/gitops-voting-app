import unittest

from app import app


class ApiUnitTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_returns_200(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_api_returns_hello(self):
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello, I am the api service", response.data)


if __name__ == "__main__":
    unittest.main()
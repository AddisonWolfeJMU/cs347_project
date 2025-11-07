from django.test import TestCase, Client
from django.contrib.auth.models import User

class UserAuthCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "securepass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_register_user(self):
        response = self.client.post("/api/register/", {
            "username": "newuser",
            "password": "newpass"
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_login_user(self):
        response = self.client.post("/api/login/", {
            "username": self.username,
            "password": self.password
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))

    def test_user_view_requires_login(self):
        response = self.client.get("/api/user/")
        self.assertNotEqual(response.status_code, 200)  # should redirect or forbid

    def test_authenticated_user_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get("/api/user/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], self.username)

    def test_update_user_requires_password(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.patch("/api/user/update/",
                                     {"username": "updateduser"},
                                     content_type="application/json")
        self.assertEqual(response.status_code, 403)  # password required

    def test_delete_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.delete("/api/user/delete/",
                                      {"password": self.password},
                                      content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=self.username).exists())

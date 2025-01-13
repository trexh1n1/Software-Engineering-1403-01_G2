import random
import string

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .urls import app_name


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse(f"{app_name}:signup")
        self.login_url = reverse(f"{app_name}:login")
        self.logout_url = reverse(f"{app_name}:logout")

        self.user_data = {
            "username": "testusername-".join(
                [
                    string.ascii_letters[random.randrange(0, len(string.ascii_letters))]
                    for _ in range(5)
                ]
            ),
            "email": "testemail@test.ir",
            "password": "TestPass123456@",
            "name": "testname",
            "age": "20",
        }

    def test_signup_endpoint(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": self.user_data["username"],
                "email": self.user_data["username"],
                "password1": self.user_data["password"],
                "password2": self.user_data["password"],
                "name": self.user_data["name"],
                "age": self.user_data["age"],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)
        follow_response = self.client.get(response.url)

        self.assertEqual(follow_response.status_code, 200)
        self.assertTrue(
            User.objects.filter(username=self.user_data["username"]).exists()
        )

    def test_login_endpoint(self):
        User.objects.create_user(
            username=self.user_data["username"], password=self.user_data["password"]
        )

        response = self.client.post(
            self.login_url,
            {
                "username": self.user_data["username"],
                "pass": self.user_data["password"],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)
        follow_response = self.client.get(response.url)

        self.assertEqual(follow_response.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_endpoint(self):
        User.objects.create_user(
            username=self.user_data["username"], password=self.user_data["password"]
        )
        self.client.login(
            username=self.user_data["username"], password=self.user_data["password"]
        )

        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 302)
        follow_response = self.client.get(response.url)

        self.assertEqual(follow_response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

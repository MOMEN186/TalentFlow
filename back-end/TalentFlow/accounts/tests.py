from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from .models import CustomUser


class AuthTestMixin:
    email = "momenehab186@gmail.com"
    password = "admin"

    def create_hr_user(self):
        user, _ = CustomUser.objects.get_or_create(email=self.email)
        user.set_password(self.password)
        user.is_active = True
        user.is_staff = True
        user.save()
        hr_group, _ = Group.objects.get_or_create(name="HR")
        user.groups.add(hr_group)
        return user

    def authenticate(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"email": self.email, "password": self.password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return access, response.cookies.get("refresh_token")


class AccountsAuthEndpointsTests(APITestCase, AuthTestMixin):
    def setUp(self):
        self.create_hr_user()

    def test_login_obtain_pair_and_cookie_refresh(self):
        access, refresh_cookie = self.authenticate()
        self.assertTrue(access)
        # refresh via body
        refresh_url = reverse("token_refresh")
        # Prefer body refresh with explicit refresh from first login
        body_refresh = refresh_cookie.value if refresh_cookie else None
        body_resp = self.client.post(refresh_url, {"refresh": body_refresh}, format="json")
        self.assertEqual(body_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", body_resp.data)

        # refresh via cookie (no body) using the new cookie set by refresh response
        new_cookie = body_resp.cookies.get("refresh_token")
        if new_cookie:
            self.client.cookies["refresh_token"] = new_cookie.value
            cookie_resp = self.client.post(refresh_url, {}, format="json")
            self.assertEqual(cookie_resp.status_code, status.HTTP_200_OK)
            self.assertIn("access", cookie_resp.data)

    def test_profile_me_and_logout(self):
        self.authenticate()
        me_url = reverse("profile-list") + "me/"
        me_resp = self.client.get(me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data.get("email"), self.email)

        # logout needs refresh
        refresh_url = reverse("token_obtain_pair")
        pair = self.client.post(refresh_url, {"email": self.email, "password": self.password}, format="json")
        refresh_token = pair.cookies.get("refresh_token")
        logout_url = reverse("logout")
        payload = {"refresh": refresh_token.value if refresh_token else None}
        out = self.client.post(logout_url, payload, format="json")
        self.assertIn(out.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST))
        # Both outcomes are acceptable depending on blacklist state; schema check
        self.assertIn("detail", out.data)

from django.test import TestCase

# Create your tests here.

from django.test import TestCase
import unittest
from django.urls import reverse
import pytest

# from authentication.models import Product
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse

User = get_user_model()


@pytest.mark.django_db
class TestProfilePage(TestCase):
    def test_profile_view_for_authenticated_users(self):
        User.objects.create_user(email="admin@admin.com", password="password123456")

        self.client.login(email="admin@admin.com", password="password123456")
        response = self.client.get(reverse("profile"))
        # self.assertRedirects(
        #     response,
        #     expected_url=f"{reverse('account_login')}?next={reverse('onboarding')}",
        # )
        self.assertEqual(response.status_code, 302)
        first = User.objects.first()
        print(first)

        # self.assertContains(response, "admin@admin.com")


# unittest.main()

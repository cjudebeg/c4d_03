from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render


User = get_user_model()


class TestProfilePage(TestCase):
    def test_profile_view_for_authenticated_users(self):
        User.objects.create_user(email="admin@admin.com", password="password")

        self.client.login(email="admin@admin.com", password="password")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        # self.save()
        all = User.objects.all()
        # print(User.objects.id)
        print(all)

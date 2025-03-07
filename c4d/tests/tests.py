# from django.contrib.auth import get_user_model
# from django.test import TestCase
# import pytest

# # from c4d.authentication.validators import MinimumLengthValidator


# class UsersManagersTests(TestCase):
#     def test_create_user(self):
#         User = get_user_model()
#         user = User.objects.create_user(email="[email protected]", password="foo")
#         self.assertEqual(user.email, "[email protected]")
#         self.assertTrue(user.is_active)
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)
#         try:
#             # username is None for the AbstractUser option
#             # username does not exist for the AbstractBaseUser option
#             self.assertIsNone(user.username)
#         except AttributeError:
#             pass
#         with self.assertRaises(TypeError):
#             User.objects.create_user()
#         with self.assertRaises(TypeError):
#             User.objects.create_user(email="")
#         with self.assertRaises(ValueError):
#             User.objects.create_user(email="", password="foo")

#     def test_create_superuser(self):
#         User = get_user_model()
#         admin_user = User.objects.create_superuser(
#             email="[email protected]", password="foo"
#         )
#         self.assertEqual(admin_user.email, "[email protected]")
#         self.assertTrue(admin_user.is_active)
#         self.assertTrue(admin_user.is_staff)
#         self.assertTrue(admin_user.is_superuser)
#         try:
#             # username is None for the AbstractUser option
#             # username does not exist for the AbstractBaseUser option
#             self.assertIsNone(admin_user.username)
#         except AttributeError:
#             pass
#         with self.assertRaises(ValueError):
#             User.objects.create_superuser(
#                 email="[email protected]", password="foo", is_superuser=False
#             )


# def test_minimum_password_length(MinimumLengthValidator):
#     User = get_user_model()
#     admin_user = User.objects.create_user(email="[email protected]", password="foo")
#     MinimumLengthValidator.validate(admin_user.email, admin_user.password)


from django.test import TestCase
from django.urls import reverse

# from django.contrib.auth.models import User
from authentication.models import Profile
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpTest(TestCase):
    def test_sign_up_page_exists(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")

    def test_sign_up_user(self):
        user_data = {
            "email": "test@email.com",
            # "username": "testuser",
            "password1": "testpassword2",
            "password2": "testpassword2",
        }
        response = self.client.post(
            reverse("account_signup"), user_data, format="text/html"
        )
        self.assertEqual(response.status_code, 302)

        # response = self.client.get(reverse("onboarding", args=[user_data["email"]]))
        # self.assertEqual(response.status_code, 200)

    def test_sign_up_user_wrong_password(self):
        user_data = {
            "email": "test@email.com",
            # "username": "testuser",
            "password1": "testpassword2",
            "password2": "testpassword",
        }
        response = self.client.post(
            reverse("account_signup"), user_data, format="text/html"
        )
        self.assertEqual(response.status_code, 200)

        # response = self.client.get(reverse("onboarding", args=[user_data["email"]]))
        # self.assertEqual(response.status_code, 200)


class BaseSetUp(TestCase):

    def setUp(self):
        user_data = {
            "email": "test2@email.com",
            # "username": "testuser",
            "password1": "testpassword2",
            "password2": "testpassword2",
        }
        self.client.post(reverse("account_signup"), user_data, format="text/html")


class ProfileEditTest(BaseSetUp):
    # def test_post_create(self):
    #     response = self.client.get(reverse("post-create"))

    def test_profile_edit(self):
        # self.client.logout()

        response = self.client.get(reverse("profile-edit"))
        self.assertEqual(response.status_code, 302)

        form_data = {"email": "test2@email.com"}

        response = self.client.post(reverse("profile-edit"), data=form_data)
        self.assertEqual(response.status_code, 302)

        self.user = User.objects.get(email="test2@email.com")
        self.assertEqual(self.user.email, "test2@email.com")

        # No data has been entered for first_name field as yet
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.first_name, None)

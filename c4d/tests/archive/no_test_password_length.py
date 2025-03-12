# import pytest
# # from tests.no_test_utils import *
# # from a_core.no_utils import *


# def test_new_user(django_user_model):
#     user = django_user_model.objects.create_user(
#         email="admin@admin.com", password="somethingsomething"
#     )
#     user.save()
#     assert user.email == "admin@admin.com"


# def test_new_user2(django_user_model):
#     user = django_user_model.objects.create_user(
#         email="admin2@admin.com", password="some"
#     )
#     user.save()
#     assert user.email == "admin2@admin.com"


# def test_new_user3(django_user_model):
#     user = django_user_model.objects.create_user(
#         email="admin3@admin.com", password="some"
#     )
#     user.save()
#     assert user.email == "admin3@admin.com"


# # def test_with_authenticated_client(client, django_user_model):
# #     email = "user1"
# #     password = "bar"
# #     user = django_user_model.objects.create_user(email=email, password=password)
# #     # Use this:
# #     client.force_login(user)
# #     response = client.get("/private")
# #     assert response.content == "Protected Area"

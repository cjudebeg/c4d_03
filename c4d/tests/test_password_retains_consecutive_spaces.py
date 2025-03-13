import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from authentication.validators import *
from django.urls import reverse
from django.contrib.auth.hashers import check_password


User = get_user_model()


def generate_password(length, char="a"):
    """Helper to generate a simple password of a given length."""
    return char * length


@pytest.mark.django_db
def test_password_retains_consecutive_spaces():
    password_with_spaces = "password    with   multiple     spaces"
    password_without_spaces = "password with multiple spaces"
    user = User.objects.create_user(
        email="test@example.com", password=password_with_spaces
    )
    # Ensure that no consecutive spaces exist in the stored password
    # assert not any(
    #     " " * n in user.password for n in range(2, len(password_with_spaces))
    # )
    assert check_password(password_with_spaces, user.password) is True
    assert check_password(password_without_spaces, user.password) is False


# @pytest.mark.django_db
# def test_user_password_matches_saved_password():
#     """Test that user-supplied password matches the stored password."""
#     user = User.objects.create_user(
#         email="test@example.com",
#         password="password    with   multiple     spaces",
#     )
#     assert (
#         check_password("password    with   multiple     spaces", user.password) is True
#     )
#     assert check_password("password with multiple spaces", user.password) is False

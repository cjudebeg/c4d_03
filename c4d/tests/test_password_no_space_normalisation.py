import pytest
import string
from django.contrib.auth import get_user_model
from authentication.validators import *
from django.contrib.auth.hashers import check_password

User = get_user_model()


@pytest.mark.django_db
def test_password_no_space_normalization():
    """
    Check that the password is not truncated when set.

    https://github.com/OWASP/ASVS/issues/1029

    The OWASP link above proposes the removal of consecutive space normalisation, as described below.
    This test checks that space normalisation is NOT PRESENT.

    However, consecutive spaces may be normalized to a single space.
    For example, the raw password "This   is    a valid   password with    spaces"
    is normalized to "This is a valid password with spaces" before validation.
    We test that the normalized password passes the check_password test.
    """
    raw_password = "This   is    a valid   password with    spaces"
    user = User.objects.create_user(email="test4@example.com", password=raw_password)
    user.full_clean()
    # Assume space normalization, if applied, would replace multiple spaces with one.
    normalized_password = "This is a valid password with spaces"
    assert not user.check_password(normalized_password)
    assert user.check_password(raw_password)


@pytest.mark.django_db
def test_password_retains_consecutive_spaces():
    password_with_spaces = "password    with   multiple     spaces"
    password_without_spaces = "password with multiple spaces"
    user = User.objects.create_user(
        email="test@example.com", password=password_with_spaces
    )
    assert check_password(password_with_spaces, user.password) is True
    assert check_password(password_without_spaces, user.password) is False

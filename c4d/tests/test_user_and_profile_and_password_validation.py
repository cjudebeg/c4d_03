import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from authentication.models import Profile  # Ensure this matches your project structure

User = get_user_model()


@pytest.fixture
def user_01(db):
    """Fixture to create a user instance for testing."""
    return User.objects.create_user(email="admin@admin.com", password="password1234")


@pytest.mark.django_db
def test_is_user_valid(user_01):
    """Test if a user instance is valid and successfully created."""
    assert user_01.email == "admin@admin.com"
    assert user_01.check_password("password1234")


@pytest.mark.django_db
def test_password_validation():
    """Test Django's built-in password validation."""
    valid_password = "Str0ngP@ssw0rd!"
    weak_password = "password"

    # Valid password should pass validation
    try:
        validate_password(valid_password)
    except ValidationError:
        pytest.fail("Valid password did not pass validation.")

    # Weak password should raise a ValidationError
    with pytest.raises(ValidationError, match="This password is too common."):
        validate_password(weak_password)


@pytest.mark.django_db
def test_profile_created_with_user(user_01):
    """Test that a Profile is automatically created when a User is created."""
    profile = Profile.objects.filter(user=user_01).first()
    assert profile is not None, "Profile should be created with user."

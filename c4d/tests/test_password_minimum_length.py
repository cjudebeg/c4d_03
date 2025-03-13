import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from authentication.validators import *
from django.urls import reverse


@pytest.mark.parametrize(
    "password,should_raise",
    [
        ("short", True),  # Too short, should raise ValidationError
        ("longenough_12", False),  # Long enough, should not raise
        ("exact_length", False),  # Exactly 12 characters (assuming min_length=12)
    ],
)
def test_minimum_password_length_validator(password, should_raise):
    validator = MinimumLengthValidator(min_length=12)  # Adjust min_length if needed

    if should_raise:
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        expected_message = ngettext(
            "This password is too short. It must contain at least "
            "%(min_length)d character.",
            "This password is too short. It must contain at least "
            "%(min_length)d characters.",
            12,
        ) % {"min_length": 12}

        assert expected_message in str(exc_info.value)
    else:
        # Should not raise any exceptions
        validator.validate(password)


@pytest.mark.django_db
def test_custom_user_model_password_length():
    """
    Ensure that a custom user model (with email as the unique identifier) enforces password length.
    """
    User = get_user_model()
    min_length = 12

    valid_password = "a" * (min_length)
    invalid_password = "a" * (min_length - 1)

    # Create a user with a valid password
    user = User.objects.create_user(
        email="testuser@example.com", password=valid_password
    )
    assert user.check_password(
        valid_password
    ), "User should be able to authenticate with a min-length password."

    # Attempt to set an invalid password and expect a validation error
    validator = MinimumLengthValidator(min_length=min_length)
    with pytest.raises(
        ValidationError,
        match="This password is too short. It must contain at least 12 characters.",
    ):
        # with pytest.raises(ValidationError, match="This password is less than the minimum"):
        validator.validate(invalid_password)

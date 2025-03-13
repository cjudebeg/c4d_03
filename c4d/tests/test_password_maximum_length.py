import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from authentication.validators import *
from django.urls import reverse


# tests the vaidator


@pytest.mark.django_db
def test_maximum_password_length_validation():
    """
    Test that MaximumLengthValidator correctly validates passwords based on length.
    """
    max_length = 128
    validator = MaximumLengthValidator(max_length=max_length)

    # Valid password (exactly at max length)
    valid_password = "a" * max_length
    try:
        validator.validate(valid_password)
    except ValidationError:
        pytest.fail(
            "Validation should not fail for a password of maximum allowed length."
        )

    # Invalid password (exceeds max length)
    invalid_password = "a" * (max_length + 1)
    with pytest.raises(
        ValidationError, match="This password is greater than the maximum"
    ):
        validator.validate(invalid_password)


# tests validation of the model


@pytest.mark.django_db
def test_custom_user_model_password_length():
    """
    Ensure that a custom user model (with email as the unique identifier) enforces password length.
    """
    User = get_user_model()
    max_length = 128

    valid_password = "a" * (max_length)
    invalid_password = "a" * (max_length + 1)

    # Create a user with a valid password
    user = User.objects.create_user(
        email="testuser@example.com", password=valid_password
    )
    assert user.check_password(
        valid_password
    ), "User should be able to authenticate with a max-length password."

    # Attempt to set an invalid password and expect a validation error
    validator = MaximumLengthValidator(max_length=max_length)
    with pytest.raises(
        ValidationError, match="This password is greater than the maximum"
    ):
        validator.validate(invalid_password)

# tests/test_custom_signup_form.py

import pytest
from django.contrib.auth.password_validation import get_default_password_validators
from django.core.exceptions import ValidationError
from authentication.forms import (
    CustomUserSignupForm,
)  # Adjust the import path as necessary


@pytest.mark.django_db
def test_custom_signup_form_invalid_password():
    """
    Test that the CustomUserSignupForm rejects a password that does not meet the
    minimum length requirement (and any other validators configured).
    """
    form_data = {
        "email": "user@example.com",
        "password1": "shortpwd",  # Too short (<12 characters)
        "password2": "shortpwd",
    }
    form = CustomUserSignupForm(data=form_data)
    assert (
        not form.is_valid()
    ), "Form should be invalid for a password that is too short."
    assert "password1" in form.errors, "Expected an error for the password1 field."


@pytest.mark.django_db
def test_custom_signup_form_valid_password():
    """
    Test that the CustomUserSignupForm accepts a valid password (one that passes all validators)
    and does not raise any validation errors.
    """
    form_data = {
        "email": "user@example.com",
        "password1": "averysecurepassword",  # Valid password (>=12 characters)
        "password2": "averysecurepassword",
    }
    form = CustomUserSignupForm(data=form_data)
    assert form.is_valid(), f"Form should be valid but got errors: {form.errors}"

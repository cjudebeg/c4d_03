import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test.client import RequestFactory
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.middleware import SessionMiddleware
from authentication.forms import (
    CustomUserSignupForm,
)  # Adjust the import path as necessary

# Import the allauth signup form
from allauth.account.forms import SignupForm


@pytest.mark.django_db
def test_password_validator_rejects_short_password():
    """
    Test that the minimum length validator (min_length=12) rejects a password
    that is too short.
    """
    short_password = "shortpwd"  # fewer than 12 characters
    with pytest.raises(ValidationError) as excinfo:
        validate_password(short_password)
    # Optionally check that the error message indicates the password is too short
    assert "This password is too short" in str(excinfo.value)


@pytest.mark.django_db
def test_password_validator_accepts_valid_password():
    """
    Test that a valid password passes the password validation.
    """
    valid_password = "averysecurepassword"  # at least 12 characters
    try:
        validate_password(valid_password)
    except ValidationError:
        pytest.fail("A valid password raised a ValidationError.")


@pytest.mark.django_db
def test_signup_form_with_invalid_password():
    """
    Test that the allauth SignupForm rejects a password that does not meet the
    minimum length requirement.
    """
    form_data = {
        "email": "user@example.com",
        "password1": "shortpwd",  # too short
        "password2": "shortpwd",
    }
    form = CustomUserSignupForm(data=form_data)
    assert not form.is_valid()
    # Check that an error on the password field is reported
    assert "password1" in form.errors


@pytest.mark.django_db
def test_signup_form_with_valid_password():
    """
    Test that the allauth SignupForm rejects a password that meets the
    minimum length requirement.
    """
    form_data = {
        "email": "user@example.com",
        "password1": "exactpasswrd",  # exact length
        "password2": "exactpasswrd",
    }
    form = CustomUserSignupForm(data=form_data)
    assert form.is_valid()
    # Check that no error on the password field is reported
    assert not "password1" in form.errors


# @pytest.mark.django_db
# def test_signup_form_with_valid_password_and_user_creation():
#     """
#     Test that the allauth SignupForm accepts a valid password and that saving the
#     form creates a User instance.
#     """
#     form_data = {
#         "email": "user@example.com",
#         "password1": "averysecurepassword",  # valid password (>=12 characters)
#         "password2": "averysecurepassword",
#     }
#     form = SignupForm(data=form_data)
#     assert form.is_valid(), form.errors

#     # Save the user. (The 'request' parameter is optional; passing None is acceptable for testing.)
#     user = form.save(request=None)
#     # Verify that the user has been saved to the database (i.e. has a primary key)
#     assert user.pk is not None
#     # Optionally, you can also check that the email was saved correctly.
#     User = get_user_model()
#     db_user = User.objects.get(pk=user.pk)
#     assert db_user.email == "user@example.com"


@pytest.mark.django_db
def test_signup_form_with_valid_password_and_user_creation():
    """
    Test that the allauth SignupForm accepts a valid password and that saving the
    form creates a User instance.
    """
    form_data = {
        "email": "user@example.com",
        "password1": "averysecurepassword",  # valid password (>=12 characters)
        "password2": "averysecurepassword",
    }
    form = CustomUserSignupForm(data=form_data)
    assert form.is_valid(), form.errors

    # Create a dummy request with a session using RequestFactory and SessionMiddleware
    rf = RequestFactory()
    request = rf.get("/")
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()

    # Save the form with the request that now has a session
    user = form.save(request=request)
    assert user.pk is not None

    User = get_user_model()
    db_user = User.objects.get(pk=user.pk)
    assert db_user.email == "user@example.com"

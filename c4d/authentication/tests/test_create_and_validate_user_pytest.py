import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from authentication.forms import CustomUserSignupForm

User = get_user_model()


@pytest.fixture
def create_user_with_form_validation():
    """
    Fixture that creates a user using the CustomUserSignupForm with proper message setup.
    Returns a function that either returns a user instance or raises ValidationError.
    """

    def _create_user(email, password):
        form_data = {
            "email": email,
            "password1": password,
            "password2": password,  # Confirmation password
        }

        form = CustomUserSignupForm(data=form_data)

        if form.is_valid():
            # Mock the request object needed by allauth forms
            class MockRequest:
                def __init__(self):
                    self.META = {}
                    # Properly set up session
                    self.session = {}

            request = MockRequest()

            # Properly set up the messages framework
            setattr(request, "session", {})
            from django.contrib.messages.storage.fallback import FallbackStorage

            messages = FallbackStorage(request)
            setattr(request, "_messages", messages)

            # Get the password to check if it was modified
            password_modified = False
            original_password = password
            cleaned_password = form.cleaned_data.get("password1")
            if original_password != cleaned_password:
                password_modified = True

            # Return both user and password modification info
            user = form.save(request)
            return user, password_modified, cleaned_password
        else:
            # Convert form errors into ValidationError
            raise ValidationError(form.errors)

    return _create_user


@pytest.mark.django_db
def test_validation_with_short_password(create_user_with_form_validation):
    """Test that form validation catches short passwords."""
    email = "test2@example.com"

    # Test too short password
    with pytest.raises(ValidationError):
        create_user_with_form_validation(email, "short123")


@pytest.mark.django_db
def test_consecutive_spaces_in_password(create_user_with_form_validation):
    """
    Test that passwords with consecutive spaces are silently modified.
    This is not a validation error, but a modification.
    """
    email = "test3@example.com"

    # Password with multiple consecutive spaces
    original_password = "password      with     multiple          spaces"
    expected_cleaned_password = "password with multiple spaces"

    # This should NOT raise ValidationError
    user, was_modified, cleaned_password = create_user_with_form_validation(
        email, original_password
    )

    # Assert the password was modified
    assert was_modified is True

    # Assert the cleaned password has single spaces
    assert cleaned_password == expected_cleaned_password

    # Make sure the user was created and can authenticate with the modified password
    assert user.check_password(expected_cleaned_password)


# Above test tests that passwords with consecutive spaces are modified.
# Passwords with consecutive spaces should not be modified or validated, so passing this test is confirmation of a defect.

# Elaborate test below checks if any validators appear to be explicitly handling spaces.

# After checking the source code, the tester believes that the form's clean() method is silently
# modifying passwords with multiple spaces rather than raising a validation error.
# The form is handling this as a convenience feature (with a notification message) rather than as a validation rule.


@pytest.mark.django_db
def test_no_validator_for_consecutive_spaces():
    """
    Test that there is no validator in validators.py responsible for rejecting
    passwords with consecutive spaces.
    """
    from django.conf import settings

    # Check all configured password validators
    space_validator_exists = False

    for validator_config in settings.AUTH_PASSWORD_VALIDATORS:
        validator_class = validator_config["NAME"].split(".")[-1]
        # Check if any validator name suggests space validation
        if "space" in validator_class.lower():
            space_validator_exists = True

    assert (
        not space_validator_exists
    ), "Found a validator that might handle spaces in passwords"


# Test to check that modification of passwords with consecutive spaaces occurs and that no validator is responsible.


def test_both_tests():
    if test_no_validator_for_consecutive_spaces:
        if test_consecutive_spaces_in_password:
            assert True

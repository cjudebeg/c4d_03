from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from authentication.forms import CustomUserSignupForm

User = get_user_model()


class UserFormValidationTestCase(TestCase):
    """Test case for validating User creation using forms."""

    def create_user_with_form_validation(self, email, password):
        """
        Fixture that creates a user using the CustomUserSignupForm.
        Returns the user instance or raises ValidationError.
        """
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
                    self.session = {}

            request = MockRequest()

            # Set up messages framework
            setattr(request, "session", {})
            messages = FallbackStorage(request)
            setattr(request, "_messages", messages)

            return form.save(request)
        else:
            # Convert form errors into ValidationError
            raise ValidationError(form.errors)

    def test_user_creation_with_valid_form(self):
        """Test creating a user with valid form data."""
        email = "test@example.com"
        password = "Str0ng_P@ssw0rd!123"

        user = self.create_user_with_form_validation(email, password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_validation_with_invalid_passwords(self):
        """Test that form validation catches invalid passwords."""
        email = "test2@example.com"

        # Test too short password
        with self.assertRaises(ValidationError):
            self.create_user_with_form_validation(email, "short123")

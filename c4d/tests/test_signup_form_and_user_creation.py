import pytest
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from authentication.forms import (
    CustomUserSignupForm,
)  # Adjust the import path as needed


@pytest.mark.django_db
def test_signup_form_with_valid_password_and_user_creation():
    """
    Test that the CustomUserSignupForm accepts a valid password and that saving the form creates a User instance.
    """
    form_data = {
        "email": "user@example.com",
        "password1": "averysecurepassword",  # Valid password (>= 12 characters)
        "password2": "averysecurepassword",
    }
    form = CustomUserSignupForm(data=form_data)
    assert form.is_valid(), form.errors

    # Create a dummy request with a session using RequestFactory and SessionMiddleware.
    rf = RequestFactory()
    request = rf.get("/")
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    # Save the form using the request with a valid session.
    user = form.save(request=request)
    assert user.pk is not None

    User = get_user_model()
    db_user = User.objects.get(pk=user.pk)
    assert db_user.email == "user@example.com"

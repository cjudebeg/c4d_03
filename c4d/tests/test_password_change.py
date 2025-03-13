import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from authentication.validators import *
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_user_can_change_password():
    """
    Test that a user can change their password.
    This test creates a user, changes the password (using Django’s set_password),
    and then verifies that the new password works while the old one does not.
    """
    original_password = "OriginalPass123!"
    new_password = "NewSecurePass456!"
    user = User.objects.create_user(
        email="test6@example.com", password=original_password
    )
    user.full_clean()
    # Change password using Django's built-in method.
    user.set_password(new_password)
    user.save()
    assert user.check_password(new_password)
    assert not user.check_password(original_password)


@pytest.mark.django_db
def test_password_change_requires_current_and_new_password():
    """
    Simulate a custom password change method that requires both the current and new passwords.
    (Typically, such logic is enforced in a view or a dedicated method.)
    Here we define a local helper function to simulate that behavior.
    """
    original_password = "ValidPass123!"
    new_password = "NewValidPass456!"
    user = User.objects.create_user(
        email="test7@example.com", password=original_password
    )
    user.full_clean()

    def change_password(user, current_password, new_password):
        if not current_password or not new_password:
            raise ValidationError("Both current and new password are required.")
        if not user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        user.set_password(new_password)
        user.save()

    # Test: missing current password.
    with pytest.raises(ValidationError):
        change_password(user, "", new_password)
    # Test: missing new password.
    with pytest.raises(ValidationError):
        change_password(user, original_password, "")
    # Test: wrong current password.
    with pytest.raises(ValidationError):
        change_password(user, "WrongPass", new_password)
    # Test: correct password change.
    change_password(user, original_password, new_password)
    assert user.check_password(new_password)

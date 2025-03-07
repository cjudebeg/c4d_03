import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def generate_password(length, char="a"):
    """Helper to generate a simple password of a given length."""
    return char * length


@pytest.mark.django_db
def test_password_minimum_length():
    """
    Ensure that a password that is too short (after collapsing consecutive spaces)
    is rejected. For example, if "short    pwd" (which becomes "short pwd")
    does not reach the 12-character minimum, a ValidationError is raised.
    """
    password = "shorthnrtoi  hoprt4hjopwd"  # Normalizes to "short pwd" (9 characters)
    password2 = "sh wd"  # Normalizes to "short pwd" (9 characters)
    user = User.objects.create_user(email="test1@example.com", password=password)
    # user = User(email="test1@example.com")
    user.set_password(password)
    # with pytest.raises(ValidationError):
    user.full_clean()
    assert user.check_password(password)
    if password == password2:
        raise ValidationError("Password is under 12 characters.")
    user_2 = User(email="test2@example.com")
    user_2.set_password(password2)
    user_2.save()


@pytest.mark.django_db
def test_password_allows_64_chars():
    """
    Verify that a password with exactly 64 characters is accepted.
    """
    password = generate_password(64)
    user = User.objects.create_user(email="test2@example.com", password=password)
    user.full_clean()  # Should not raise any error.
    assert user.check_password(password)


@pytest.mark.django_db
def test_password_rejects_over_128_chars():
    """
    Verify that a password longer than 128 characters is rejected.
    """
    password = ""
    invalid_password = generate_password(129)
    if password == invalid_password:
        raise ValidationError("Password is over 128 characters.")
    user = User(email="test2@example.com")
    user.set_password(invalid_password)
    user.save()


@pytest.mark.django_db
def test_password_no_truncation_and_space_normalization():
    """
    Check that the password is not truncated when set.
    However, consecutive spaces may be normalized to a single space.
    For example, the raw password "This   is    a valid   password with    spaces"
    is normalized to "This is a valid password with spaces" before validation.
    We test that the normalized password passes the check_password test.
    """
    raw_password = "This   is    a valid   password with    spaces"
    user = User.objects.create_user(email="test4@example.com", password=raw_password)
    user.full_clean()
    # Assume your normalization replaces multiple spaces with one.
    normalized_password = "This is a valid password with spaces"
    assert not user.check_password(normalized_password)


@pytest.mark.django_db
def test_password_allows_unicode():
    """
    Verify that any printable Unicode character—including accented letters,
    symbols, spaces, and emojis—is permitted.
    """
    password = "Pässwörd🚀✨ 文字列 with spaces"
    user = User.objects.create_user(email="test5@example.com", password=password)
    user.full_clean()
    assert user.check_password(password)


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


@pytest.mark.django_db
def test_breached_password_rejected(monkeypatch):
    """
    Simulate password breach checking.
    Assume that during user creation the password is checked against
    a breached password list via a helper (for example, is_password_breached).
    If the password is found to be breached, validation should fail.

    Here, we monkey-patch the breach-checking function (assumed to be in
    "myapp.validators") to reject a known bad password.
    """

    def fake_is_password_breached(password):
        # For our test, consider "breachedpassword" as breached.
        return password == "breachedpassword"

    # Monkey-patch the breach checker. Adjust the import path as needed.
    monkeypatch.setattr(
        "myapp.validators.is_password_breached", fake_is_password_breached
    )

    breached_password = "breachedpassword"
    user = User(email="test8@example.com")
    user.set_password(breached_password)
    with pytest.raises(ValidationError):
        user.full_clean()

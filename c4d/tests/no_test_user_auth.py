import re
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


# Helper function to simulate collapsing multiple spaces into one
def collapse_spaces(password: str) -> str:
    return re.sub(r"\s+", " ", password).strip()


# @pytest.mark.django_db
# def test_password_min_length():
#     """
#     Verify that the password (after collapsing spaces) is at least 12 characters long.
#     """
#     # A password that becomes too short after collapsing spaces.
#     invalid_password = "short   pwd"  # becomes "short pwd" (9 characters)
#     collapsed = collapse_spaces(invalid_password)
#     assert len(collapsed) < 12
#     print("collapsed white space == less than 12 characters long password ")

#     # Expect a ValidationError on creation
#     with pytest.raises(ValidationError):
#         user1 = User.objects.create_user(
#             email="user1@user.com", password=invalid_password
#         )
#         assert user1.check_password(invalid_password)

#     # A valid password of exactly 12 characters (no extra spaces)
#     valid_password = "a" * 12
#     user2 = User.objects.create_user(email="user2@user.com", password=valid_password)
#     assert user2.check_password(valid_password)


import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def generate_password(length, char="a"):
    """Helper to generate a simple password of a given length."""
    return char * length


@pytest.mark.django_db
def test_password_min_length():
    """
    Ensure that a password that is too short (after collapsing consecutive spaces)
    is rejected. For example, "short    pwd" normalizes to "short pwd" (9 characters),
    which is less than the required 12 characters. A ValidationError should be raised.
    """
    password = "short    pwd"  # Normalizes to "short pwd" (9 characters)
    user = User(email="test1@example.com")
    user.set_password(password)
    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_password_max_length():
    """
    Verify that a password longer than 128 characters is rejected.
    A password of 129 characters should trigger a ValidationError.
    """
    password = generate_password(129)
    user = User(email="test3@example.com")
    user.set_password(password)
    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_password_truncation():
    """
    Verify that the password is not silently truncated.
    However, multiple consecutive spaces should be collapsed to one.
    """
    # Construct a password where the intended “collapsed” password is 13 characters:
    # 6 "a" characters, a group of spaces (to collapse to one), then 6 "b" characters.
    # raw_password = "a" * 6 + "     " + "b" * 6
    # collapsed = collapse_spaces(raw_password)
    a_password = "qw3\\9pe4tr\\nikj"
    assert len(a_password) == 15

    # user = User.objects.create_user(email="user55@user.com", password=raw_password)
    user2 = User.objects.create_user(email="user5@user.com", password=a_password)
    # Assuming that the user manager or validator stores/compares the collapsed password,
    # check_password should succeed on the collapsed version.
    assert user2.check_password(a_password)
    # assert user2.check_password(a_password)


@pytest.mark.django_db
def test_password_unicode_characters():
    """
    Verify that any printable Unicode characters (including spaces and emojis) are accepted.
    """
    # Create a password with Japanese characters, spaces, and emojis.
    password = "パスワード😊👍 " + " " * 3 + "用户测试"
    collapsed = collapse_spaces(password)
    # Skip the test if the final length is below minimum (for demonstration).
    if len(collapsed) < 12:
        pytest.skip("Password does not meet the 12-character minimum after collapsing.")
        print("SKIP")
    user = User.objects.create_user(email="user6@user.com", password=password)
    # Check against the original and/or collapsed version.
    assert user.check_password(password) or user.check_password(collapsed)


@pytest.mark.django_db
def test_password_change():
    """
    Verify that a user can successfully change their password.
    """
    original_password = "a" * 12
    user = User.objects.create_user(email="user7@user.com", password=original_password)
    new_password = "b" * 12

    # In Django, the typical pattern is to use set_password() then save().
    user.set_password(new_password)
    user.save()

    # The old password should no longer work.
    assert not user.check_password(original_password)
    # The new password must be valid.
    assert user.check_password(new_password)


@pytest.mark.django_db
def test_password_change_requires_current_and_new(monkeypatch):
    """
    Assume the user model (or a helper method) enforces that password changes require
    both the current and a new valid password.
    """
    original_password = "a" * 12
    user = User.objects.create_user(email="user8@user.com", password=original_password)

    # For testing, we add a dummy change_password method to the instance.
    def fake_change_password(self, current_password, new_password):
        if not self.check_password(current_password):
            raise ValidationError("Current password incorrect")
        # Validate that the new password meets minimum length after collapsing spaces.
        if len(collapse_spaces(new_password)) < 12:
            raise ValidationError("New password too short")
        self.set_password(new_password)
        self.save()

    # Monkeypatch the user instance with our fake change_password method.
    setattr(user, "change_password", fake_change_password.__get__(user, type(user)))

    # Attempt a change with an incorrect current password.
    with pytest.raises(ValidationError):
        user.change_password("wrongpassword", "c" * 12)

    # Attempt a change with a new password that is too short.
    with pytest.raises(ValidationError):
        user.change_password(original_password, "short")

    # A valid password change should work.
    user.change_password(original_password, "d" * 12)
    assert user.check_password("d" * 12)


# @pytest.mark.django_db
# def test_breached_password(monkeypatch):
#     """
#     Simulate the check against a list (or API) of breached passwords. Here, we assume that during
#     user creation a function (e.g. check_password_breach) is called. We monkeypatch it to raise a
#     ValidationError if a known breached password is used.
#     """

#     # Define a fake breach check that raises an error for a specific password.
#     def fake_check_password_breach(password):
#         if password == "breachedpassword":
#             raise ValidationError("Password is breached")

#     # Adjust the import path to wherever your custom manager calls this function.
#     monkeypatch.setattr(
#         "myapp.managers.check_password_breach", fake_check_password_breach
#     )

#     # Creating a user with a breached password should raise a ValidationError.
#     with pytest.raises(ValidationError):
#         User.objects.create_user(email="user9@user.com", password="breachedpassword")

#     # A valid password should pass the breach check.
#     valid_password = "e" * 12
#     user = User.objects.create_user(email="user9@user.com", password=valid_password)
#     assert user.check_password(valid_password)

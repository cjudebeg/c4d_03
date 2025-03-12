# import pytest
# import string
# from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
# from django.utils.translation import ngettext
# from authentication.validators import *
# from django.urls import reverse

# User = get_user_model()


# def generate_password(length, char="a"):
#     """Helper to generate a simple password of a given length."""
#     return char * length


# @pytest.mark.django_db
# def test_breached_password_rejected(monkeypatch):
#     """
#     Simulate password breach checking.
#     Assume that during user creation the password is checked against
#     a breached password list via a helper (for example, is_password_breached).
#     If the password is found to be breached, validation should fail.

#     Here, we monkey-patch the breach-checking function (assumed to be in
#     "myapp.validators") to reject a known bad password.
#     """

#     def fake_is_password_breached(password):
#         # For our test, consider "breachedpassword" as breached.
#         return password == "breachedpassword"

#     # Monkey-patch the breach checker. Adjust the import path as needed.
#     monkeypatch.setattr(
#         "authentication.validators.is_password_breached", fake_is_password_breached
#     )

#     breached_password = "breachedpassword"
#     user = User(email="test8@example.com")
#     user.set_password(breached_password)
#     with pytest.raises(ValidationError):
#         user.full_clean()

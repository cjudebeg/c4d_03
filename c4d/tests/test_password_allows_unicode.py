import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from authentication.validators import *
from django.urls import reverse

User = get_user_model()


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

    # if user.check_password(password) == True:
    #     # print(" UNICODE ALLOWED ")

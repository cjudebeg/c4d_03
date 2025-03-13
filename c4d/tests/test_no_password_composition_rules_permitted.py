import pytest
import string
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from authentication.validators import *
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


@pytest.mark.django_db
def test_no_password_composition_rules_permitted():

    min_valid_length = 12

    # There should be no requirement for upper or lower case or numbers or special characters

    no_comp_rules_all_lower_no_special = "a" * min_valid_length
    no_comp_rules_all_upper_no_special = "A" * min_valid_length
    no_comp_rules_all_special = "Pässwörd🚀✨ 文字列 with spaces"

    # Create a user with a valid password
    user = User.objects.create_user(
        email="testuser@example.com", password=no_comp_rules_all_lower_no_special
    )
    assert user.check_password(
        no_comp_rules_all_lower_no_special
    ), "User should be able to validate with all lower case."

    user_01 = User.objects.create_user(
        email="testuser_01@example.com", password=no_comp_rules_all_upper_no_special
    )

    assert user_01.check_password(
        no_comp_rules_all_upper_no_special
    ), "User should be able to validate with all upper case."

    user_02 = User.objects.create_user(
        email="testuser_02@example.com", password=no_comp_rules_all_special
    )

    assert user_02.check_password(
        no_comp_rules_all_special
    ), "User should be able to authenticate with all special character."


@pytest.mark.django_db
def test_no_password_composition_rules():
    """Test that passwords with no composition rules are still considered valid."""
    min_length = 12
    under_length = 11

    # Variables for different password types
    no_comp_rules_all_lower_no_special = "a" * min_length
    no_comp_rules_all_upper_no_special = "A" * min_length
    no_comp_rules_all_special = "!@#$%^&*()_+="  # 12 special characters
    invalid_password = "a" * under_length  # Less than min_length

    # Valid passwords should pass validation
    for password in [
        no_comp_rules_all_lower_no_special,
        no_comp_rules_all_upper_no_special,
        no_comp_rules_all_special,
    ]:
        try:
            validate_password(password)
        except ValidationError:
            pytest.fail(f"Valid password '{password}' did not pass validation.")

    # Weak password should raise a ValidationError
    with pytest.raises(ValidationError, match="This password is too short."):
        validate_password(invalid_password)

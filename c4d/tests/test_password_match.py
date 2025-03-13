import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
def test_user_password_matches_saved_password():
    """Test that user-supplied password matches the stored password."""
    user = User.objects.create_user(
        email="test@example.com", password="SecurePassword123!"
    )
    assert check_password("SecurePassword123!", user.password) is True
    assert check_password("SecurePassword321!", user.password) is False

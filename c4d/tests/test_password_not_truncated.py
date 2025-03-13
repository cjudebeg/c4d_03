import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()


@pytest.mark.django_db
def test_password_not_truncated():
    """Ensure that passwords are not truncated when stored in the database."""
    long_password = "A" * 128  # 128-character password
    user = User.objects.create_user(email="test@example.com", password=long_password)
    assert check_password(long_password, user.password) is True


# @pytest.mark.django_db
# def test_password_does_not_contain_consecutive_spaces():
#     """Ensure that passwords do not contain consecutive blank spaces."""
#     password_with_spaces = "password    with   spaces"
#     user = User.objects.create_user(
#         email="test@example.com", password=password_with_spaces
#     )
#     # Check that consecutive spaces are normalized to single spaces
#     assert "  " not in user.password  # Ensure no double spaces in the stored password


# @pytest.mark.django_db
# def test_user_password_matches_saved_password_with_consecutive_blanks():
#     """Test that user-supplied password matches the stored password."""
#     user = User.objects.create_user(
#         email="test@example.com", password="space  in  password"
#     )
#     assert check_password("space  in  password", user.password) is True
#     assert user.check_password("space  in  password")

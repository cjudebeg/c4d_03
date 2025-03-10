import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture()
def user_01(db):
    user = User.objects.create_user("admin@admin.com", "password1234")
    return user


@pytest.fixture()
def user_02(db):
    user = User.objects.create_user("admin2@admin.com", "ktyhj")
    return user


def test_check_email(user_01):
    assert user_01.email == "admin@admin.com"
    assert user_01.email != "admin@email.com"


@pytest.mark.django_db
def test_my_user_password(user_01):
    user_01.set_password("password1234")
    assert user_01.check_password("password1234") is True
    assert user_01.check_password("pa34") is False

    # User.objects.create_user("admin@admin.com", "password1234")
    # assert user.email == "admin@admin.com"


@pytest.mark.django_db
def test_my_user_password2(user_02):
    user_02.set_password("ktyhj")
    assert user_02.check_password("ktyhj") is True
    # assert user_02.check_password("pa34") is False

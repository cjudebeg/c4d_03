import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user_factory(db):
    def create_app_user(
        # username: str,
        # first_name: str = "firstname",
        # last_name: str = "lastname",
        email: str = "email@email.com",
        password: str = None,
        is_staff: str = False,
        is_superuser: str = False,
        is_active: str = True,
    ):
        user = User.objects.create_user(
            # username=username,
            # first_name=first_name,
            # last_name=last_name,
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        return user

    return create_app_user


@pytest.fixture
def user_a(db, user_factory):
    return user_factory("email@email.com", "password")


def test_new_user(user_a):
    print(user_a.is_active)
    assert user_a.email == "email@email.com"

# c4d/authentication/tests/test_password_validation.py
from django.test import TestCase
from string import ascii_lowercase, ascii_uppercase, digits, punctuation, whitespace
from a_core.utils import is_valid_password, contains_character, is_valid_size
import pytest

valid_chars = set(punctuation)


def get_invalid_chars():
    invalid_chars = set(punctuation + whitespace) - valid_chars
    return "".join(invalid_chars)


def get_valid_chars():
    return "".join(valid_chars)


class PasswordValidationTests(TestCase):

    def test_valid_password(self):
        """Test passwords that should be valid"""
        passwords = ["6o6SC/5}d$_=", "u694[B{+('Xhj", "Tw8I47-v}a[#U8"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertTrue(
                    is_valid_password(password), f"{password} should be valid"
                )

    def test_short_password(self):
        """Test passwords that are shorter than the requirement"""
        passwords = ["2_20mAJeviw", "Jv41|7M5#w"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} is too short. Minimum requirement is 12 characters",
                )

    def test_long_password(self):
        """Test passwords that are too long"""
        passwords = [
            "{qA{oq:MX%Q'DlM6@j;[3sB~=9x$fqZ1Nvfn=7\\O8o>oTM9G9X#_y'+u/C=~5sdXvXpI",  # 68 characters
            "84)Z+^@b4$|+l>2=if&k&1|^r3R$`JTKSzrYtL\\a^R+Sg9#9!hn>|55-_ymqoCG?hmSK'",  # 70 characters
            "ukhk4uiLXiNvgK=XS5\\7g[]hdn`_([>9myk?5NRE~bRE^D*^UT2r0WcF[>GVUKM/xqx4EHe",  # 71 characters
        ]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it is longer than the requirement",
                )

    def test_password_missing_uppercase(self):
        """Test passwords missing an uppercase letter"""
        passwords = ["lowercase1@password", "1234567890abcdefg@"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it is missing an uppercase letter",
                )

    def test_password_missing_special_character(self):
        """Test passwords missing a special character"""
        passwords = ["NoSpecialChar1", "PasswordWithoutSpecial123"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it is missing a special character",
                )

    def test_password_missing_lowercase(self):
        """Test passwords missing a lowercase letter"""
        passwords = ["UPPERCASE1@PASSWORD", "1234567890ABCDEFG@"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it is missing a lowercase letter",
                )

    def test_password_missing_digit(self):
        """Test passwords missing a digit"""
        passwords = ["NoDigits@Here", "PasswordWithoutDigits!"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it is missing a digit",
                )

    def test_password_with_invalid_character(self):
        """Test passwords with invalid characters"""
        passwords = ["Invalid;Char1", "InvalidPassword;123"]
        for password in passwords:
            with self.subTest(password=password):
                self.assertFalse(
                    is_valid_password(password),
                    f"{password} should be invalid because it contains an invalid character (semicolon)",
                )

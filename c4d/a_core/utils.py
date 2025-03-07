# a_core/utils.py
import re
from string import ascii_lowercase, ascii_uppercase, digits, punctuation, whitespace
import pytest

valid_chars = set(punctuation)


def contains_character(password: str = "", sack: str = "") -> bool:
    has_char = False
    for char in password:
        if char in sack:
            has_char = True
            break
    return has_char


def is_valid_size(password: str = "") -> bool:
    MIN_SIZE = 12
    MAX_SIZE = 128
    password_size = len(password)
    return MIN_SIZE <= password_size <= MAX_SIZE


def get_invalid_chars():
    invalid_chars = set(punctuation + whitespace) - valid_chars
    return "".join(invalid_chars)


def get_valid_chars():
    return "".join(valid_chars)


def is_valid_password(password: str = "") -> bool:
    try:
        if not password:
            return False
        new_password = password.strip()
        if not is_valid_size(new_password):
            return False
        if not contains_character(new_password, ascii_lowercase):
            return False
        if not contains_character(new_password, ascii_uppercase):
            return False
        if not contains_character(new_password, digits):
            return False
        if contains_character(new_password, get_invalid_chars()):
            return False
        if not contains_character(new_password, get_valid_chars()):
            return False
        return True
    except:
        return False

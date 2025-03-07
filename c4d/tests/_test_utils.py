# c4d/authentication/tests/test_utils.py
from django.test import TestCase
from a_core.utils import contains_character, is_valid_size
from django.contrib.auth import get_user_model
import pytest

# from django.core.exceptions import ValidationError

User = get_user_model()


class UtilsTests(TestCase):

    def test_contains_character(self):
        """Test the contains_character function"""
        self.assertFalse(
            contains_character("", ""), "Empty password and sack should return False"
        )
        self.assertFalse(
            contains_character("i", "python"), "'i' in 'python' should return False"
        )
        self.assertTrue(
            contains_character("py", "python"), "'py' in 'python' should return True"
        )
        self.assertTrue(
            contains_character("python", "python"),
            "'python' in 'python' should return True",
        )

    def test_is_valid_size(self):
        """Test the is_valid_size function"""
        self.assertFalse(is_valid_size(""), "Empty password should return False")
        self.assertFalse(
            is_valid_size("p@4S"), "4 character password should return False"
        )
        self.assertFalse(
            is_valid_size("hD-^e;S7&81"), "11 character password should return False"
        )
        self.assertTrue(
            is_valid_size("TZVF(7Fa2GrE"), "12 character password should return True"
        )
        self.assertTrue(
            is_valid_size("re]HJu%Q:\\;?c"), "13 character password should return True"
        )
        # self.assertTrue(
        #     is_valid_size(
        #         "fYm-!!q<r1ZmmOF>:3(pW344_kt,qm8B^z]zU'#==|yxX7j:Q\\TsYmtHr#mK;jp*;ZPZ"
        #     ),
        #     "68 character password should return True",
        # )
        self.assertTrue(
            is_valid_size(
                "hp*\\5s5.X@:iRd&0l$=-1/!-.VaiN,xG/OO>DG3Elk=mS)dgOOu~6R)8`((O%^<Nd6X:r/"
            ),
            "128 character password should return True",
        )
        self.assertFalse(
            is_valid_size(
                "hp*\\5s5.X@:iRd&0l$=-1/!-.VaiNu,xG/OO>DG3Elk=mS)dgOOu~6R)8`((O%^<Nd6X:r/"
            ),
            "129 character password should return False",
        )

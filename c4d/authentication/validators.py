from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _, ngettext
import re


class NewPasswordNotSameAsOldValidator:
    def validate(self, password, user=None):
        if user and user.check_password(password):
            raise ValidationError(
                _("The new password cannot be the same as your current password."),
                code="password_no_change",
            )

    def get_help_text(self):
        return _("Your new password must be different from your current password.")


class MaximumLengthValidator:

    def __init__(self, max_length=128):

        self.max_length = max_length

    def validate(self, password, user=None):

        if len(password) > self.max_length:

            raise ValidationError(
                _(
                    "This password is greater than the maximum of %(max_length)d characters."
                ),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):

        return _(
            "Your password can be a maximum of %(max_length)d characters."
            % {"max_length": self.max_length}
        )


# ====================


class OneSpaceValidator:
    """
    Ensures that consecutive spaces in the password are replaced by a single space.
    """

    def validate(self, password, user=None):
        # Check if the password has multiple consecutive spaces
        if re.search(r"\s{2,}", password):  # Matches two or more consecutive spaces
            raise ValidationError(
                "Your password cannot contain consecutive spaces.",
                code="password_multiple_spaces",
            )

    def get_help_text(self):
        return "Your password cannot contain consecutive spaces; only single spaces are allowed."


class UsernamePasswordSimilarityValidator:
    """
    Ensures that the password is not too similar to the username.
    """

    def __init__(self, max_similarity=0.4):
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if user and user.username:
            similarity = self._calculate_similarity(password, user.username)
            if similarity >= self.max_similarity:
                raise ValidationError(
                    "The password is too similar to the username.",
                    code="password_too_similar",
                )

    def get_help_text(self):
        return "Your password cannot be too similar to your username."

    def _calculate_similarity(self, password, username):
        matches = sum(1 for x, y in zip(password, username) if x == y)
        return matches / max(len(password), len(username))


# class BreachPasswordValidator:
#     """
#     Checks if the given password has been breached using the Have I Been Pwned API.
#     """

#     def validate(self, password, user=None):
#         sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
#         prefix = sha1_password[:5]
#         url = f'https://api.pwnedpasswords.com/range/{prefix}'
#         response = requests.get(url)

#         if response.status_code != 200:
#             raise ValidationError("Error checking password security. Please try again.")

#         suffix = sha1_password[5:]
#         if any(line.split(':')[0] == suffix for line in response.text.splitlines()):
#             raise ValidationError("This password has been compromised in a data breach. Please choose a different one.")

#     def get_help_text(self):
#         return "Your password must not have been compromised in a data breach."


class UnicodePasswordValidator:
    def validate(self, password, user=None):
        if not re.match(
            r"^[\s\w\W]+$", password
        ):  # Allows all Unicode and whitespace characters
            raise ValidationError(
                "Your password must allow any Unicode character, including emojis."
            )

    def get_help_text(self):
        return "Your password can contain any character, including Unicode and emojis."


class MinimumLengthValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "This password is too short. It must contain at least "
                    "%(min_length)d character.",
                    "This password is too short. It must contain at least "
                    "%(min_length)d characters.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_length)d character.",
            "Your password must contain at least %(min_length)d characters.",
            self.min_length,
        ) % {"min_length": self.min_length}


# def exceeds_maximum_length_ratio(password, max_similarity, value):
#     """
#     Test that value is within a reasonable range of password.

#     The following ratio calculations are based on testing SequenceMatcher like
#     this:

#     for i in range(0,6):
#       print(10**i, SequenceMatcher(a='A', b='A'*(10**i)).quick_ratio())

#     which yields:

#     1 1.0
#     10 0.18181818181818182
#     100 0.019801980198019802
#     1000 0.001998001998001998
#     10000 0.00019998000199980003
#     100000 1.999980000199998e-05

#     This means a length_ratio of 10 should never yield a similarity higher than
#     0.2, for 100 this is down to 0.02 and for 1000 it is 0.002. This can be
#     calculated via 2 / length_ratio. As a result we avoid the potentially
#     expensive sequence matching.
#     """
#     pwd_len = len(password)
#     length_bound_similarity = max_similarity / 2 * pwd_len
#     value_len = len(value)
#     return pwd_len >= 10 * value_len and value_len < length_bound_similarity

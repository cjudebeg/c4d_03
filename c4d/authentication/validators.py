from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.utils.translation import ngettext, gettext as _, gettext_lazy as _
from django.utils.deconstruct import deconstructible
import re

# from difflib import SequenceMatcher


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


# class UserAttributeSimilarityValidator:
#     """
#     Validate that the password is sufficiently different from the user's
#     attributes.

#     If no specific attributes are provided, look at a sensible list of
#     defaults. Attributes that don't exist are ignored. Comparison is made to
#     not only the full attribute value, but also its components, so that, for
#     example, a password is validated against either part of an email address,
#     as well as the full address.
#     """

#     DEFAULT_USER_ATTRIBUTES = ("username", "first_name", "last_name", "email")

#     def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
#         self.user_attributes = user_attributes
#         if max_similarity < 0.1:
#             raise ValueError("max_similarity must be at least 0.1")
#         self.max_similarity = max_similarity

#     def validate(self, password, user=None):
#         if not user:
#             return

#         password = password.lower()
#         for attribute_name in self.user_attributes:
#             value = getattr(user, attribute_name, None)
#             if not value or not isinstance(value, str):
#                 continue
#             value_lower = value.lower()
#             value_parts = re.split(r"\W+", value_lower) + [value_lower]
#             for value_part in value_parts:
#                 if exceeds_maximum_length_ratio(
#                     password, self.max_similarity, value_part
#                 ):
#                     continue
#                 if (
#                     SequenceMatcher(a=password, b=value_part).quick_ratio()
#                     >= self.max_similarity
#                 ):
#                     try:
#                         verbose_name = str(
#                             user._meta.get_field(attribute_name).verbose_name
#                         )
#                     except FieldDoesNotExist:
#                         verbose_name = attribute_name
#                     raise ValidationError(
#                         _("The password is too similar to the %(verbose_name)s."),
#                         code="password_too_similar",
#                         params={"verbose_name": verbose_name},
#                     )

#     def get_help_text(self):
#         return _(
#             "Your password can’t be too similar to your other personal information."
#         )


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


# class NormalizeConsecutiveSpacesValidator:
#     """
#     Custom password validator that normalizes consecutive blank spaces to a single space.
#     """

#     def validate(self, password, user=None):
#         if "  " in password:  # Check if there are consecutive spaces
#             raise ValidationError(
#                 _(
#                     "Your password contains consecutive spaces, which will be normalized."
#                 ),
#                 code="consecutive_spaces",
#             )

#     def get_help_text(self):
#         return _("Your password should not contain consecutive blank spaces.")


# def normalize_password(password):
#     """
#     Normalize a password by replacing consecutive blank spaces with a single space.
#     """
#     return re.sub(r"\s+", " ", password)


# ====================


# class OneSpaceValidator:
#     """
#     Ensures that consecutive spaces in the password are replaced by a single space.
#     If consecutive spaces are found, we inform the user accordingly.
#     """

#     def validate(self, password, user=None):
#         # Replace two or more consecutive spaces with a single space
#         new_password = re.sub(r"\s{2,}", " ", password)
#         if new_password != password:
#             # Let the user know we replaced consecutive spaces
#             raise ValidationError(
#                 _(
#                     "We replaced consecutive spaces with a single space in your password."
#                 ),
#                 code="password_multiple_spaces",
#             )

#     def get_help_text(self):
#         return _(
#             "Your password cannot contain consecutive spaces; they will be replaced by a single space."
#         )


# class UsernamePasswordSimilarityValidator:
#     """
#     Ensures that the email is not too similar to the password.
#     """

#     def __init__(self, max_similarity=0.4):
#         self.max_similarity = max_similarity

#     def validate(self, password, user=None):
#         if user and user.email:
#             similarity = self._calculate_similarity(password, user.email)
#             if similarity >= self.max_similarity:
#                 raise ValidationError(
#                     "The password is too similar to the email.",
#                     code="password_too_similar",
#                 )

#     def get_help_text(self):
#         return "Your password cannot be too similar to your email."

#     def _calculate_similarity(self, password, email):
#         matches = sum(1 for x, y in zip(password, email) if x == y)
#         return matches / max(len(password), len(email))


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
                    "%(min_length)d characters.",
                    "This password is too short. It must contain at least "
                    "%(min_length)d characters.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_length)d characters.",
            "Your password must contain at least %(min_length)d characters.",
            self.min_length,
        ) % {"min_length": self.min_length}

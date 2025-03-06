from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re
from django.utils.deconstruct import deconstructible

class NewPasswordNotSameAsOldValidator:
    def validate(self, password, user=None):
        if user and user.check_password(password):
            raise ValidationError(
                _("The new password cannot be the same as your current password."),
                code='password_no_change',
            )

    def get_help_text(self):
        return _("Your new password must be different from your current password.")


class MaximumLengthValidator:

    def __init__(self, max_length=128):

        self.max_length = max_length

    def validate(self, password, user=None):

        if len(password) > self.max_length:

            raise ValidationError(

                _("This password is greater than the maximum of %(max_length)d characters."),

                code='password_too_long',

                params={'max_length': self.max_length},

            )

    def get_help_text(self):

        return _(

            "Your password can be a maximum of %(max_length)d characters."

            % {'max_length': self.max_length}

        ) 
    



 # ====================

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class OneSpaceValidator:
    """
    Ensures that consecutive spaces in the password are replaced by a single space.
    If consecutive spaces are found, we inform the user accordingly.
    """

    def validate(self, password, user=None):
        # Replace two or more consecutive spaces with a single space
        new_password = re.sub(r'\s{2,}', ' ', password)
        if new_password != password:
            # Let the user know we replaced consecutive spaces
            raise ValidationError(
                _("We replaced consecutive spaces with a single space in your password."),
                code='password_multiple_spaces'
            )

    def get_help_text(self):
        return _("Your password cannot contain consecutive spaces; they will be replaced by a single space.")


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
                    code='password_too_similar',
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
        if not re.match(r'^[\s\w\W]+$', password):  # Allows all Unicode and whitespace characters
            raise ValidationError("Your password must allow any Unicode character, including emojis.")
        
    def get_help_text(self):
        return "Your password can contain any character, including Unicode and emojis."
   
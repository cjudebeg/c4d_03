from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class NewPasswordNotSameAsOldValidator:
    def validate(self, password, user=None):
        if user and user.check_password(password):
            raise ValidationError(
                _("The new password cannot be the same as your current password."),
                code='password_no_change',
            )

    def get_help_text(self):
        return _("Your new password must be different from your current password.")

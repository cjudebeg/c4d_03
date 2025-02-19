from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.apps import apps

class AutoUsernameAccountAdapter(DefaultAccountAdapter):
    # Generates username from the user's email.

    def save_user(self, request, user, form, commit=True):
        # Called by Allauth after a successful signup/superuser creation.
        # Ensures user.username is set to a unique value derived from user.email.
        user = super().save_user(request, user, form, commit=False)
        
        if not user.username:
            base_username = user.email.split('@')[0]
            final_username = base_username
            i = 1

            # Its to ensure uniqueness
            UserModel = apps.get_model(settings.AUTH_USER_MODEL)
            while UserModel.objects.filter(username=final_username).exists():
                final_username = f"{base_username}{i}"
                i += 1

            user.username = final_username

        if commit:
            user.save()
        return user

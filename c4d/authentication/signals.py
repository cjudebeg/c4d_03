# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from .models import Profile
# from django.core.mail import send_mail
# from django.contrib.auth import get_user_model

# User = get_user_model()


# @receiver(post_save, sender=User)
# def create_or_update_profile(sender, instance, created, **kwargs):
#     print("signal fired")
#     if created:
#         Profile.objects.create(user=instance)
#         send_mail(
#             "Welcome!",
#             "Thanks for signing up!",
#             "admin@django.com",
#             [instance.email],
#             fail_silently=False,
#         )
#     else:
#         instance.profile.save()  # Save/update profile for existing user

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()  # Save/update profile for existing user

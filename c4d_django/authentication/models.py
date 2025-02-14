from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

SECURITY_CLEARANCE_CHOICES = [
    ('None', 'None'),
    ('Pending', 'Pending'),
    ('Baseline', 'Baseline'),
    ('Negative Vetting 1', 'Negative Vetting 1'),
    ('Negative Vetting 2', 'Negative Vetting 2'),
    ('Positive Vetting', 'Positive Vetting'),
]

class CustomUser(AbstractUser):
    username = None  # Removing the username field
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    agvsa_clearance_number = models.CharField(max_length=50, blank=True, null=True)
    security_clearance = models.CharField(
        max_length=20,
        choices=SECURITY_CLEARANCE_CHOICES,
        default='None'
    )
    suburb = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.email}"


# Signal to automatlly create / update the Profile whenever a CustomUser is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

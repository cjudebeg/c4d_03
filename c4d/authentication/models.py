from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):

    # Custom User model that uses email as the primary identifier. Users reg with email and pwd.

    # username = models.CharField(max_length=150, unique=True)
    # email = models.EmailField(_('email address'), unique=True)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']  # This forces createsuperuser to ask for username

    # def __str__(self):
    #     return self.email
    pass


STATE_CHOICES = [
    ('VIC', 'VIC'),
    ('NSW', 'NSW'),
    ('ACT', 'ACT'),
    ('QLD', 'QLD'),
    ('NT', 'NT'),
    ('WA', 'WA'),
    ('SA', 'SA'),
]

CLEARANCE_LEVEL_CHOICES = [
    ('None', 'None'),
    ('Pending', 'Pending'),
    ('Baseline', 'Baseline'),
    ('NV1', 'NV1'),
    ('NV2', 'NV2'),
    ('PV', 'PV'),
]


class Profile(models.Model):
    # Link profile to the Customuser model one to one
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=30, blank=True, null=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    state = models.CharField(max_length=3, choices=STATE_CHOICES, blank=True, null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)

    clearance_level = models.CharField(max_length=20, choices=CLEARANCE_LEVEL_CHOICES, blank=True, null=True)
    clearance_no = models.CharField(max_length=50, blank=True, null=True)
    clearance_expiry = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

# Automatically create/update profile when a customUser is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  
    else:
        instance.profile.save()  # Save/update profile for existing user

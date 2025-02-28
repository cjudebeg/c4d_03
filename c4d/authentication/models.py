import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    # Custom user model that uses email as the primary identifier
    # Users reg with email and pwd

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()

    def __str__(self):
        return self.email


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
    # Link profile to the customuser model one to one
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

    # displayname = models.CharField(max_length=100, blank=True, null=True)


    skill_sets = models.TextField(blank=True, null=True)
    skill_level = models.CharField(max_length=100, blank=True, null=True)

    # New field for tracking onboarding
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.email}"

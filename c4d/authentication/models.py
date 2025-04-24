"""
Adds pending-name-change fields directly on Profile so requests are
stored with the profile.
"""

import uuid
from django.conf                import settings
from django.contrib.auth.models import AbstractUser
from django.db                  import models
from django.utils.translation   import gettext_lazy as _
from .managers                  import CustomUserManager


STATE_CHOICES: list[tuple[str, str]] = [
    ("VIC", "VIC"), ("NSW", "NSW"), ("ACT", "ACT"), ("QLD", "QLD"),
    ("NT",  "NT"),  ("WA",  "WA"),  ("SA",  "SA"),
]

CLEARANCE_LEVEL_CHOICES: list[tuple[str, str]] = [
    ("None",     "None"),
    ("Pending",  "Pending"),
    ("Baseline", "Baseline"),
    ("NV1",      "NV1"),
    ("NV2",      "NV2"),
    ("PV",       "PV"),
]

CLEARANCE_VALID_CHOICES: list[tuple[str, str]] = [
    ("PENDING", "Pending"),
    ("YES",     "Yes"),
    ("NO",      "No"),
]


class CustomUser(AbstractUser):
    """
    Email-as-username custom user model.
    """
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email    = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD   = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

    def __str__(self) -> str:   # pragma: no cover
        return self.email


class Profile(models.Model):
    """
    One-to-one companion model for CustomUser.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name="profile")

    # personal
    first_name    = models.CharField(max_length=30, blank=True, null=True)
    middle_name   = models.CharField(max_length=30, blank=True, null=True)
    last_name     = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # location
    state  = models.CharField(max_length=3,
                              choices=STATE_CHOICES,
                              blank=True,
                              null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)

    # clearance
    clearance_level        = models.CharField(max_length=20,
                                              choices=CLEARANCE_LEVEL_CHOICES,
                                              blank=True,
                                              null=True)
    clearance_no           = models.CharField(max_length=50, blank=True, null=True)
    clearance_revalidation = models.DateField(blank=True, null=True)
    clearance_valid        = models.CharField(max_length=7,
                                              choices=CLEARANCE_VALID_CHOICES,
                                              default="PENDING")
    clearance_active       = models.BooleanField(default=False)

    # skills / onboarding
    skill_sets           = models.TextField(blank=True, null=True)
    skill_level          = models.CharField(max_length=100, blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)

    # pending-name-change (no extra table)
    pending_first_name     = models.CharField(max_length=30, blank=True, null=True)
    pending_middle_name    = models.CharField(max_length=30, blank=True, null=True)  # ← NEW
    pending_last_name      = models.CharField(max_length=30, blank=True, null=True)
    pending_name_reason    = models.TextField(blank=True, null=True)
    pending_name_requested = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:   # pragma: no cover
        return f"Profile of {self.user.email}"

    def clear_pending_name(self) -> None:
        """
        Helper so admins can clear a request quickly.
        """
        self.pending_first_name  = None
        self.pending_middle_name = None
        self.pending_last_name   = None
        self.pending_name_reason = None
        self.pending_name_requested = None
        self.save(update_fields=[
            "pending_first_name",
            "pending_middle_name",
            "pending_last_name",
            "pending_name_reason",
            "pending_name_requested",
        ])

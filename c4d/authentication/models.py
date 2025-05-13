"""
Models for user profile and job functionality.
"""

import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager


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

    def __str__(self) -> str:
        return self.email


class Profile(models.Model):
    """
    One-to-one companion model for CustomUser.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # personal
    first_name    = models.CharField(max_length=30, blank=True, null=True)
    middle_name   = models.CharField(max_length=30, blank=True, null=True)
    last_name     = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # location
    state  = models.CharField(
        max_length=3,
        choices=STATE_CHOICES,
        blank=True,
        null=True
    )
    suburb = models.CharField(max_length=100, blank=True, null=True)

    # clearance
    clearance_level        = models.CharField(
        max_length=20,
        choices=CLEARANCE_LEVEL_CHOICES,
        blank=True,
        null=True
    )
    clearance_no           = models.CharField(max_length=50, blank=True, null=True)
    clearance_revalidation = models.DateField(blank=True, null=True)
    clearance_valid        = models.CharField(
        max_length=7,
        choices=CLEARANCE_VALID_CHOICES,
        default="PENDING"
    )
    clearance_active       = models.BooleanField(default=False)

    # skills / onboarding
    skill_sets           = models.TextField(blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)

    # pending-name-change (no extra table)
    pending_first_name     = models.CharField(max_length=30, blank=True, null=True)
    pending_middle_name    = models.CharField(max_length=30, blank=True, null=True)
    pending_last_name      = models.CharField(max_length=30, blank=True, null=True)
    pending_name_reason    = models.TextField(blank=True, null=True)
    pending_name_requested = models.DateTimeField(blank=True, null=True)

    # ← NEW FLAG FOR ADMIN
    name_change_done       = models.BooleanField(
        default=False,
        help_text="Set to True by admin once a pending name-change request has been processed."
    )

    def __str__(self) -> str:
        return f"Profile of {self.user.email}"

    def clear_pending_name(self) -> None:
        """
        Helper so admins can clear a request quickly.
        """
        self.pending_first_name     = None
        self.pending_middle_name    = None
        self.pending_last_name      = None
        self.pending_name_reason    = None
        self.pending_name_requested = None
        self.name_change_done       = False
        self.save(update_fields=[
            "pending_first_name",
            "pending_middle_name",
            "pending_last_name",
            "pending_name_reason",
            "pending_name_requested",
            "name_change_done",
        ])


# --------- JOB RELATED MODELS ---------- #

class Rfqt(models.Model):
    """
    Request for Quotation and Tasking Statement
    """
    rfqts_no = models.CharField(max_length=200, default='RFQ-0000')  
    department = models.CharField(max_length=200, default='General')  
    group = models.CharField(max_length=200, default='Default Group')  
    directorate = models.CharField(max_length=200, default='Default Directorate')  
    project_section = models.CharField(max_length=200, default='Default Project Section') 
    task_title = models.CharField(max_length=200, default='Default Task Title') 
    commencement_date_for_task = models.DateField(null=True, blank=True)  
    completion_date_for_task = models.DateField(null=True, blank=True)  
    rfqts_type = models.CharField(max_length=200, default='General')  
    closing_date_for_quotation = models.DateField(null=True, blank=True)
    skills_sets = models.TextField(default='Default Skills Set')  
    skills_levels = models.CharField(max_length=200, default='Entry Level')  
    service_category = models.CharField(max_length=200, default='Default Service Category')  
    scope_of_task = models.TextField(default='Default Scope') 
    location = models.CharField(max_length=50, default='ACT')  
    deliverables = models.TextField(default='Default Deliverables')
    specified_personnel = models.TextField(default='Not Specified')
    evaluation_criteria = models.TextField(default="evaluate")  
    applicable_standards_or_references = models.TextField(default='None') 
    allowances_or_disbursements = models.TextField(default='None') 
    other_relevant_information_or_special_requirements = models.TextField(default='None')  
    special_conditions = models.TextField(default='None')  
    extension_options = models.TextField(default='None')  
    security_clearances_required_for_personnel = models.TextField(default='None')  
    quote_form_type = models.CharField(max_length=200, default='Standard')
    rfq_file = models.FileField(upload_to='rfq_files/', blank=True, null=True)

    class Meta:
        verbose_name = "Request for Quotation and Tasking Statement"
        verbose_name_plural = "Request for Quotation and Tasking Statements"   

    def __str__(self):
        return self.rfqts_no


class Job(models.Model):
    """
    Job listing model
    """
    JOB_TYPES = [
        ('Contract', 'Contract'),
        ('Permanent', 'Permanent'),
        ('Part-time', 'Part-time'),
        ('Casual', 'Casual'),
        ('ICT', 'ICT'),
        ('Engineering', 'Engineering'),
        ('Management', 'Management'),
        ('Accounting', 'Accounting'),
    ]

    LOCATIONS = STATE_CHOICES + [
        ('Brisbane', 'Brisbane'),
        ('Canberra', 'Canberra'),
        ('Remote', 'Remote'),
    ]

    rfqts_no = models.ForeignKey(Rfqt, related_name='jobs', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=200, help_text="Brief summary shown in the job list")
    description = models.TextField()
    location = models.CharField(max_length=50, choices=LOCATIONS, default='ACT')
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='Contract')
    salary = models.CharField(max_length=100, default='Negotiable')
    clearance = models.CharField(max_length=20, choices=CLEARANCE_LEVEL_CHOICES, default='None')
    skills_sets = models.TextField(blank=True, null=True)
    skills_levels = models.CharField(max_length=100, blank=True, null=True)
    commencement_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-submission_date']

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    """
    Job application model
    """
    APPLICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Reviewing', 'Reviewing'),
        ('Interviewed', 'Interviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, related_name="applications", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="applications", on_delete=models.CASCADE)
    rfqts_no = models.ForeignKey(Rfqt, related_name="applications", on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)  
    current_clearance = models.CharField(max_length=200, verbose_name="Current Level of Defence Clearance")  
    clearance_expiry_date = models.DateField(null=True, blank=True, verbose_name="Defence Clearance Expiry Date")  
    clearance_number = models.CharField(max_length=200, verbose_name="AGVSA CS Number", blank=True)  
    location_of_residence = models.CharField(max_length=200) 
    date_of_birth = models.DateField(null=True, blank=True)  
    earliest_start_date = models.DateField(null=True, blank=True, verbose_name="Earliest Start Date")  
    proposed_rate = models.CharField(max_length=200, blank=True, verbose_name="Proposed Contract Rate")  
    proposed_salary = models.CharField(max_length=200, blank=True, verbose_name="Proposed Annual Salary")  
    planned_leave = models.CharField(max_length=200, blank=True, verbose_name="Any Planned Leave") 
    available_for_interview = models.CharField(max_length=200, default='Yes') 
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=APPLICATION_STATUS, default="Pending")

    def __str__(self):
        return f"Application for {self.job.title} by {self.full_name}"


class Message(models.Model):
    """
    Messages between users about job applications
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(JobApplication, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} for job {self.job.title if self.job else 'General'}"
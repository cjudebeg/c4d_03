from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser, Profile, Job, JobApplication, Rfqt, Message
from .forms import CustomUserChangeForm


# ──────── customize the admin date widget to use a UK locale ────────
class AdminDMYDateWidget(AdminDateWidget):
    """
    Admin date picker, but forces British-English calendar labels
    and DD/MM/YYYY formatting.
    """
    class Media:
        js = [
            "admin/js/calendar-en-gb.js",     # UK date-picker strings
            "admin/js/calendar.js",           # core calendar logic
            "admin/js/admin/DateTimeShortcuts.js",
        ]

    def __init__(self, attrs=None, format=None):
        # show dd/mm/yyyy
        super().__init__(attrs=attrs, format="%d/%m/%Y")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )


class PendingNameFilter(admin.SimpleListFilter):
    title = _("Pending name change")
    parameter_name = "pending_name_requested"

    def lookups(self, request, model_admin):
        return [("yes", _("Has pending request")), ("no", _("No request"))]

    def queryset(self, request, qs):
        if self.value() == "yes":
            return qs.filter(pending_name_requested__isnull=False,
                             name_change_done=False)
        if self.value() == "no":
            return qs.filter(pending_name_requested__isnull=True)
        return qs


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for user profiles with UK‐style date picker.
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "clearance_revalidation":
            kwargs["widget"] = AdminDMYDateWidget()
            kwargs["input_formats"] = ["%d/%m/%Y"]
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(user__is_superuser=True)

    list_display = (
        "user",
        "clearance_no",
        "clearance_valid",
        "clearance_active",
        "clearance_level",
        "pending_first_name",
        "pending_middle_name",
        "pending_last_name",
        "pending_name_reason",
        "pending_name_requested",
        "name_change_done",
    )
    list_editable = (
        "clearance_valid",
        "clearance_active",
        "clearance_level",
        "name_change_done",
    )
    list_filter = (PendingNameFilter,)
    readonly_fields = (
        "user",
        "pending_first_name",
        "pending_middle_name",
        "pending_last_name",
        "pending_name_reason",
        "pending_name_requested",
    )
    fieldsets = (
        (None, {"fields": ("user",)}),
        ("Personal", {
            "fields": ("first_name", "middle_name", "last_name", "state", "suburb")
        }),
        ("Clearance", {
            "fields": (
                ("clearance_no", "clearance_level"),
                ("clearance_valid", "clearance_active"),
                "clearance_revalidation",
            )
        }),
        ("Skills", {"fields": ("skill_sets",)}),
        ("Pending name-change request", {
            "fields": (
                "pending_first_name",
                "pending_middle_name",
                "pending_last_name",
                "pending_name_reason",
                "pending_name_requested",
                "name_change_done",
            )
        }),
    )


# Job-related admin classes

class JobInline(admin.TabularInline):
    model = Job
    extra = 0
    fields = ('title', 'location', 'job_type', 'salary', 'is_active')


@admin.register(Rfqt)
class RfqtAdmin(admin.ModelAdmin):
    list_display = ('rfqts_no', 'task_title', 'department', 'closing_date_for_quotation')
    search_fields = ('rfqts_no', 'task_title', 'department')
    list_filter = ('department', 'rfqts_type')
    fieldsets = (
        ('Basic Information', {
            'fields': ('rfqts_no', 'task_title', 'department', 'group', 'directorate', 'project_section')
        }),
        ('Dates', {
            'fields': ('commencement_date_for_task', 'completion_date_for_task', 'closing_date_for_quotation')
        }),
        ('Requirements', {
            'fields': ('skills_sets', 'skills_levels', 'service_category', 'location')
        }),
        ('Task Details', {
            'fields': ('scope_of_task', 'deliverables', 'specified_personnel', 'evaluation_criteria')
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': (
                'applicable_standards_or_references', 'allowances_or_disbursements',
                'other_relevant_information_or_special_requirements', 'special_conditions',
                'extension_options', 'security_clearances_required_for_personnel',
                'quote_form_type', 'rfq_file'
            )
        }),
    )
    inlines = [JobInline]


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    fields = ('user', 'full_name', 'status', 'submission_date')
    readonly_fields = ('submission_date',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'clearance', 'salary', 'is_active', 'application_count')
    list_filter = ('is_active', 'job_type', 'location', 'clearance')
    search_fields = ('title', 'description', 'short_description')
    list_editable = ('is_active',)
    actions = ['mark_active', 'mark_inactive']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'short_description', 'description', 'rfqts_no')
        }),
        ('Job Details', {
            'fields': ('job_type', 'location', 'salary', 'clearance', 'is_active')
        }),
        ('Skills and Requirements', {
            'fields': ('skills_sets', 'skills_levels')
        }),
        ('Dates', {
            'fields': ('commencement_date', 'completion_date', 'closing_date')
        }),
    )
    inlines = [JobApplicationInline]
    
    def application_count(self, obj):
        count = obj.applications.count()
        return format_html('<a href="/admin/applications/?job__id__exact={}">{} application(s)</a>', obj.id, count)
    
    application_count.short_description = "Applications"
    
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
    
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    
    mark_active.short_description = "Mark selected jobs as active"
    mark_inactive.short_description = "Mark selected jobs as inactive"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job_title', 'current_clearance', 'location_of_residence', 'submission_date', 'status')
    list_filter = ('status', 'current_clearance', 'job__title')
    search_fields = ('full_name', 'user__email', 'job__title')
    readonly_fields = ('submission_date',)
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'user', 'status', 'submission_date')
        }),
        ('Personal Details', {
            'fields': ('full_name', 'date_of_birth', 'location_of_residence')
        }),
        ('Clearance Information', {
            'fields': ('current_clearance', 'clearance_expiry_date', 'clearance_number')
        }),
        ('Job Details', {
            'fields': ('earliest_start_date', 'proposed_rate', 'proposed_salary', 'planned_leave', 'available_for_interview')
        }),
        ('Application Materials', {
            'fields': ('cover_letter', 'resume')
        }),
    )
    
    def job_title(self, obj):
        return obj.job.title
    
    job_title.short_description = "Job"
    job_title.admin_order_field = "job__title"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'job_reference', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('content', 'sender__email', 'recipient__email')
    readonly_fields = ('timestamp',)
    
    def job_reference(self, obj):
        if obj.job:
            return obj.job.title
        return "General"
    
    job_reference.short_description = "Related Job"
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Profile
from .forms import CustomUserChangeForm


# ──────── customise the admin date widget to use a UK locale ────────
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
    form         = CustomUserChangeForm
    model        = CustomUser
    list_display = ("email", "is_staff", "is_active")
    list_filter  = ("is_staff", "is_active")
    search_fields= ("email",)
    ordering     = ("email",)
    fieldsets    = (
        (None,              {"fields": ("email", "password")}),
        ("Permissions",     {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email","password1","password2","is_staff","is_active"),
        }),
    )


class PendingNameFilter(admin.SimpleListFilter):
    title          = _("Pending name change")
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
            kwargs["widget"]        = AdminDMYDateWidget()
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

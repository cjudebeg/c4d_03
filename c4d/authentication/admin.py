from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from .forms  import CustomUserChangeForm
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form         = CustomUserChangeForm
    model        = CustomUser
    list_display = ("email", "is_staff", "is_active")
    list_filter  = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering     = ("email",)

    fieldsets = (
        (None,              {"fields": ("email", "password")}),
        ("Permissions",     {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


class PendingNameFilter(admin.SimpleListFilter):
    title          = _("Pending name change")
    parameter_name = "pending_name_requested"

    def lookups(self, request, model_admin):
        return [
            ("yes", _("Has pending request")),
            ("no",  _("No request")),
        ]

    def queryset(self, request, qs):
        if self.value() == "yes":
            # only those with a pending request and not yet marked done
            return qs.filter(pending_name_requested__isnull=False, name_change_done=False)
        if self.value() == "no":
            # no request at all
            return qs.filter(pending_name_requested__isnull=True)
        return qs


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        # hide superuser profiles
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
        (None,        {"fields": ("user",)}),
        ("Personal",  {"fields": ("first_name", "middle_name", "last_name", "state", "suburb")}),
        ("Clearance", {"fields": (
            ("clearance_no", "clearance_level"),
            ("clearance_valid", "clearance_active"),
            "clearance_revalidation",
        )}),
        ("Skills",    {"fields": ("skill_sets", "skill_level")}),
        ("Pending name-change request", {
            # always visible so admin can act on it immediately
            "fields": (
                "pending_first_name",
                "pending_middle_name",
                "pending_last_name",
                "pending_name_reason",
                "pending_name_requested",
                "name_change_done",  # ← allow admin to flag processing complete
            )
        }),
    )

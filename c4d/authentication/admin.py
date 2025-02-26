from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from .forms import CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm  # Form used in admin for user updates
    model = CustomUser

    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('email', 'is_staff', 'is_active')

    # Fields displayed during user editing
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields displayed when adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    
    search_fields = ('email',)
    ordering = ('email',)

class ProfileAdmin(admin.ModelAdmin):

    # Custom admin for Profile that exclude profiles belonging to superuser
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(user__is_superuser=True)

# Register the custom user model and Profile with the custom admin.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)

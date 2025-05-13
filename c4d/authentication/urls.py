from django.urls import path
from .views import (
    # Basic views
    home_view,
    
    # User account and profile views
    onboarding_view,
    profile_view,
    profile_emailchange,
    profile_emailverify,
    profile_delete_view,
    mfa_setup,
    mfa_verify,
    mfa_resend,
    CustomSignupView,
    CustomPasswordChangeView,
    update_account_view,
    update_personal_view,
    update_security_view,
    update_skills_view,
    request_name_change_view,
    
    # Job-related views
    dashboard_view,
    job_list_view,
    job_detail_view,
    job_apply_view,
    job_application_success,
    my_applications_view,
    application_detail_view,
    mark_message_as_read,
    
    # Admin job views
    admin_job_list,
    admin_job_create,
    admin_job_edit,
    admin_job_delete,
    admin_applications,
    admin_update_application_status,
)

from django.views.generic import TemplateView


urlpatterns = [
    # Home page - root URL
    path('', home_view, name='home'),
    
    # Profile and account management
    path('profile/', profile_view, name='profile'),
    path('onboarding/', onboarding_view, name='onboarding'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Override allauth signup & password-change
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/password/change/', CustomPasswordChangeView.as_view(), name='account_change_password'),

    path('profile/emailchange/', profile_emailchange, name='profile-emailchange'),
    path('profile/emailverify/', profile_emailverify, name='profile-emailverify'),
    path('profile/delete/', profile_delete_view, name='profile-delete'),

    # MFA endpoints
    path('mfa/setup/', mfa_setup, name='mfa_setup'),
    path('mfa/verify/', mfa_verify, name='mfa_verify'),
    path('mfa/resend/', mfa_resend, name='mfa_resend'),

    # Inline update endpoints
    path('profile/account/update/', update_account_view, name='profile_update_account'),
    path('profile/personal/update/', update_personal_view, name='profile_update_personal'),
    path('profile/security/update/', update_security_view, name='profile_update_security'),
    path('profile/skills/update/', update_skills_view, name='profile_update_skills'),

    # name-change request
    path('profile/name-change/request/', request_name_change_view, name='profile_request_name_change'),
    
    # Job-related URLs
    path('jobs/', job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', job_detail_view, name='job_detail'),
    path('jobs/<int:job_id>/apply/', job_apply_view, name='apply_job'),
    path('jobs/application-success/', job_application_success, name='job_application_success'),
    path('my-applications/', my_applications_view, name='my_applications'),
    path('applications/<int:application_id>/', application_detail_view, name='application_detail'),
    
    path('api/messages/<int:message_id>/read/', mark_message_as_read, name='mark_message_as_read'),
    
    # Admin job management
    path('admin/jobs/', admin_job_list, name='admin_job_list'),
    path('admin/jobs/create/', admin_job_create, name='admin_job_create'),
    path('admin/jobs/<int:job_id>/edit/', admin_job_edit, name='admin_job_edit'),
    path('admin/jobs/<int:job_id>/delete/', admin_job_delete, name='admin_job_delete'),
    path('admin/applications/', admin_applications, name='admin_applications'),
    path('admin/applications/<int:application_id>/status/', admin_update_application_status, name='admin_update_application_status'),
]
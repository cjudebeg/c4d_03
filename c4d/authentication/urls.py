from django.urls import path
from .views import (
    onboarding_view,
    profile_view,
    profile_emailchange,
    profile_emailverify,
    profile_delete_view,
    mfa_setup,
    mfa_verify,
    mfa_resend,
    CustomSignupView,
    update_account_view,
    update_personal_view,
    update_security_view,
    update_skills_view,
    request_name_change_view,
)

urlpatterns = [
    path('profile/',                    profile_view,               name='profile'),
    path('onboarding/',                 onboarding_view,            name='onboarding'),
    path('accounts/signup/',            CustomSignupView.as_view(), name='account_signup'),

    path('profile/emailchange/',        profile_emailchange,        name='profile-emailchange'),
    path('profile/emailverify/',        profile_emailverify,        name='profile-emailverify'),
    path('profile/delete/',             profile_delete_view,        name='profile-delete'),

    path('mfa/setup/',                  mfa_setup,                  name='mfa_setup'),
    path('mfa/verify/',                 mfa_verify,                 name='mfa_verify'),
    path('mfa/resend/',                 mfa_resend,                 name='mfa_resend'),

    # Inline update endpoints
    path('profile/account/update/',     update_account_view,        name='profile_update_account'),
    path('profile/personal/update/',    update_personal_view,       name='profile_update_personal'),
    path('profile/security/update/',    update_security_view,       name='profile_update_security'),
    path('profile/skills/update/',      update_skills_view,         name='profile_update_skills'),

    # AJAX name-change request
    path('profile/name-change/request/',
         request_name_change_view,
         name='profile_request_name_change'),
]

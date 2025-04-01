from django.urls import path
from .views import onboarding_view, profile_view, profile_edit_view, profile_emailchange, profile_emailverify, profile_delete_view, mfa_setup, mfa_verify, mfa_resend, CustomSignupView
#from .views import register_view, login_view
from . import views


urlpatterns = [
    # path('login/', login_view, name='login'),
    # path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('onboarding/', onboarding_view, name='onboarding'),

    path("profile/edit/", views.profile_edit_view, name="profile-edit"),

    path("onboarding/", profile_edit_view, name="profile-onboarding"),
    # path("settings/", profile_settings_view, name="profile-settings"),

    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),

    path("profile/emailchange/", profile_emailchange, name="profile-emailchange"),
    path("emailverify/", profile_emailverify, name="profile-emailverify"),
    path("delete/", profile_delete_view, name="profile-delete"),

    path('profile/email/change/', views.profile_emailchange, name='profile-emailchange'),
    path('profile/email/verify/', views.profile_emailverify, name='profile-emailverify'),

    path("mfa/setup/", mfa_setup, name="mfa_setup"),
    path("mfa/verify/", mfa_verify, name="mfa_verify"),
    path("mfa/resend/", mfa_resend, name="mfa_resend"),
    
]









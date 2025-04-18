from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from .forms import ProfileUpdateForm, EmailForm, CustomUserSignupForm
from .models import Profile
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# For MFA
from django.core.mail import send_mail
import random, string, time  

from allauth.account.views import SignupView


class CustomSignupView(SignupView):
    form_class = CustomUserSignupForm
    template_name = "account/signup.html" 

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


@login_required
def mfa_setup(request):
    for msg in list(messages.get_messages(request)):
        if "successfully signed in" not in msg.message.lower():
            messages.add_message(request, msg.level, msg.message)
    user = request.user
    code = "".join(random.choices(string.digits, k=6))
    now = int(time.time())
    request.session["mfa_code"] = code
    request.session["mfa_confirmed"] = False
    request.session["mfa_code_generated_at"] = now
    request.session["mfa_code_expires_at"] = now + 600
    send_mail(
        subject="Your MFA Code",
        message=f"Your MFA code is: {code}\n\nThis code is valid for 10 minutes.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "mfa@c4defence.com.au"),
        recipient_list=[user.email],
    )
    messages.info(request, "An OTP has been sent to your registered email address.")
    return redirect("mfa_verify")


@login_required
def mfa_verify(request):
    now = int(time.time())
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        code_in_session = request.session.get("mfa_code")
        expires_at = request.session.get("mfa_code_expires_at", 0)
        if now > expires_at:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect("mfa_resend")
        if code_in_session and token == code_in_session:
            request.session["mfa_confirmed"] = True
            del request.session["mfa_code"]
            del request.session["mfa_code_generated_at"]
            del request.session["mfa_code_expires_at"]
            messages.success(request, "MFA verification successful.")
            return redirect("profile")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    resend_wait = 0
    otp_resend_available = False
    code_generated = request.session.get("mfa_code_generated_at")
    if code_generated:
        elapsed = now - code_generated
        if elapsed >= 60:
            otp_resend_available = True
        else:
            resend_wait = 60 - elapsed
    context = {
        "otp_resend_available": otp_resend_available,
        "resend_wait": resend_wait,
        "otp_remaining": request.session.get("mfa_code_expires_at", now) - now,
    }
    return render(request, "account/mfa_verify.html", context)


@login_required
def mfa_resend(request):
    now = int(time.time())
    code_generated = request.session.get("mfa_code_generated_at", 0)
    if now - code_generated < 60:
        messages.error(request, "You cannot resend OTP until 1 minute has passed.")
        return redirect("mfa_verify")
    user = request.user
    code = "".join(random.choices(string.digits, k=6))
    request.session["mfa_code"] = code
    request.session["mfa_code_generated_at"] = now
    request.session["mfa_code_expires_at"] = now + 600
    send_mail(
        subject="Your MFA Code",
        message=f"Your new MFA code is: {code}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "mfa@c4defence.com.au"),
        recipient_list=[user.email],
    )
    messages.info(request, "A new OTP has been sent to your registered email address.")
    return redirect("mfa_verify")


@login_required
def onboarding_view(request):
    if not request.session.get("mfa_confirmed", False):
        return redirect("mfa_setup")
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user)
    if profile.onboarding_completed:
        return redirect("profile")
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.onboarding_completed = True
            profile.save()
            return redirect("profile")
        else:
            for error_msg in form.errors.get("__all__", []):
                messages.error(request, error_msg)
    else:
        form = ProfileUpdateForm(instance=profile)
    context = {
        "form": form,
        "onboarding": True,
        "user": request.user,
    }
    return render(request, "users/onboarding.html", context)


@login_required
def profile_view(request, username=None):
    if not request.session.get("mfa_confirmed", False):
        return redirect("mfa_setup")
    if username:
        profile = get_object_or_404(settings.AUTH_USER_MODEL, username=username).profile
    else:
        try:
            profile = request.user.profile
        except ObjectDoesNotExist:
            return redirect_to_login(request.get_full_path())
    if not profile.onboarding_completed:
        return redirect("onboarding")
    return render(request, "users/profile.html", {"profile": profile})


# --- INLINE UPDATE VIEWS FOR INLINE EDITING ---

@login_required
def update_account_view(request):
    user = request.user
    if request.method == "POST":
        new_email = request.POST.get('email', '').strip()
        if not new_email:
            messages.error(request, "Email is required.")
            return redirect("profile")
        if user.email.lower() == new_email.lower():
            messages.error(request, "This is already your current email address.")
            return redirect("profile")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from allauth.account.models import EmailAddress
        if (User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists() or
            EmailAddress.objects.filter(email__iexact=new_email).exclude(user=user).exists()):
            messages.error(request, f"{new_email} is already in use by an account.")
            return redirect("profile")
        EmailAddress.objects.filter(user=user).delete()
        user.email = new_email
        user.save()
        send_email_confirmation(request, user)
        messages.success(request, "Email updated! Verification email sent.")
        return redirect("profile")
    return redirect("profile")


@login_required
def update_personal_view(request):
    profile = request.user.profile
    if request.method == "POST":
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.suburb = request.POST.get('suburb', profile.suburb)
        state_full = request.POST.get('state', profile.state)
        STATE_MAP = {
            "New South Wales": "NSW",
            "Victoria": "VIC",
            "Queensland": "QLD",
            "Western Australia": "WA",
            "South Australia": "SA",
            "Tasmania": "TAS",
            "Northern Territory": "NT",
            "Australian Capital Territory": "ACT",
        }
        profile.state = STATE_MAP.get(state_full, state_full[:3])
        profile.save()
        messages.success(request, "Personal information updated.")
        return redirect("profile")
    return redirect("profile")


@login_required
def update_security_view(request):
    profile = request.user.profile
    if request.method == "POST":
        profile.clearance_level = request.POST.get('clearance_level', profile.clearance_level)
        profile.save()
        messages.success(request, "Security clearance information updated.")
        return redirect("profile")
    return redirect("profile")


@login_required
def update_skills_view(request):
    profile = request.user.profile
    if request.method == "POST":
        # "skill_sets_multiple" is the name of the multi-select field
        chosen_skills = request.POST.getlist('skill_sets_multiple', [])
        # For example: ["Consulting & Advisory", "HR & Workforce", ...]
        # Convert to a comma-separated string for storing in profile.skill_sets
        profile.skill_sets = ", ".join(chosen_skills)

        profile.skill_level = request.POST.get('skill_level', profile.skill_level)
        profile.save()
        messages.success(request, "Skill information updated.")
        return redirect("profile")
    return redirect("profile")



@login_required
def profile_emailchange(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if request.user.email.lower() == email.lower():
                return JsonResponse({
                    'success': False,
                    'message': "This is already your current email address."
                })
            from django.contrib.auth import get_user_model
            User = get_user_model()
            from allauth.account.models import EmailAddress
            if (User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists() or
                EmailAddress.objects.filter(email__iexact=email).exclude(user=request.user).exists()):
                return JsonResponse({
                    'success': False,
                    'message': f"{email} is already in use by an account."
                })
            EmailAddress.objects.filter(user=request.user).delete()
            user = request.user
            user.email = email
            user.save()
            send_email_confirmation(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Email updated! Verification email sent.',
                'email': email
            })
        else:
            error_message = "Invalid email address."
            if form.errors.get('email'):
                error_message = form.errors['email'][0]
            return JsonResponse({
                'success': False,
                'message': error_message
            })
    return redirect("profile")


@login_required
@require_POST
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return JsonResponse({
        'success': True,
        'message': 'Verification email sent.'
    })


@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity")
        return redirect("home")
    return render(request, "users/profile_delete.html")


def home_view(request):
    return render(request, "home.html")

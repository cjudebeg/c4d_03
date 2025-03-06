from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from .forms import ProfileUpdateForm, EmailForm
from .models import Profile
from django.db import IntegrityError

# from .forms import CustomUserChangeForm, LoginForm

# def register_view(request):
#     try:
#         if request.method == "POST":
#             form = CustomUserChangeForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 return redirect("login")
#             else:
#                 print("Registration form errors:", form.errors)  
#         else:
#             form = CustomUserChangeForm()
#         return render(request, "register.html", {"form": form})
    
#     except IntegrityError as e:  # Handles duplicate email issues
#         print(f"Database error: {e}")
#         form.add_error("email", "This email is already registered.")
#         return render(request, "register.html", {"form": form})
    
#     except Exception as e:  # Catch-all for unexpected errors
#         print(f"Unexpected error in register_view: {e}")
#         return render(request, "register.html", {"form": form, "error": "Something went wrong. Please try again."})


# def login_view(request):
#     try:
#         if request.method == "POST":
#             form = LoginForm(request.POST)
#             if form.is_valid():
#                 email = form.cleaned_data.get("email")
#                 password = form.cleaned_data.get("password")

#                 # USERNAME = 'email'
#                 user = authenticate(request, username=email, password=password)
#                 if user is not None:
#                     login(request, user)
#                     return redirect("profile")
#                 else:
#                     form.add_error(None, "Invalid credentials. Please try again.")
#         else:
#             form = LoginForm()
#         return render(request, "login.html", {"form": form})
    
#     except Exception as e:
#         print(f"Unexpected error in login_view: {e}")
#         return render(request, "login.html", {"form": form, "error": "Something went wrong. Please try again."})


@login_required
def onboarding_view(request):
    # Get/create the profile for the current user
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
            # If the form is invalid: capture any nonfield error and shows it as a message
            if "__all__" in form.errors:
                for error_msg in form.errors["__all__"]:
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
    if username:
        profile = get_object_or_404(settings.AUTH_USER_MODEL, username=username).profile
    else:
        try:
            profile = request.user.profile
        except ObjectDoesNotExist:
            return redirect_to_login(request.get_full_path())

    # If the user has not finished onboarding, force them
    if not profile.onboarding_completed:
        return redirect("onboarding")

    return render(request, "users/profile.html", {"profile": profile})

@login_required
def profile_edit_view(request):
    if request.path == reverse("profile-onboarding"):
        onboarding = True
    else:
        onboarding = False

    form = ProfileUpdateForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
        else:
            # If the form is invalid, capture nonfielderrors and display them via message
            if "__all__" in form.errors:
                for error_msg in form.errors["__all__"]:
                    messages.error(request, error_msg)

    return render(request, "users/profile_edit.html", {"form": form, "onboarding": onboarding})

@login_required
def profile_emailchange(request):
    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, "partials/email_form.html", {"form": form})

    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if (
                settings.AUTH_USER_MODEL.objects.filter(email=email)
                .exclude(id=request.user.id)
                .exists()
            ):
                messages.warning(request, f"{email} is already in use.")
                return redirect("profile-settings")

            form.save()
            send_email_confirmation(request, request.user)
            return redirect("profile-settings")
        else:
            messages.warning(request, "Form not valid")
            return redirect("profile-settings")

    return redirect("home")

@login_required
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return redirect("profile-settings")

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
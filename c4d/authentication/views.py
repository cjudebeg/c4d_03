from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .forms import ProfileUpdateForm


@login_required  
def profile_view(request):
    try:
        # Try to get the profile for the current user
        profile = request.user.profile
    except ObjectDoesNotExist:
        return render(request, "profile.html", {
            "error": "Profile data is missing. Please contact support or register again."
        })

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            return redirect("profile")
    else:
        # For GET requests load the form with existing data
        form = ProfileUpdateForm(instance=profile)

    context = {
        "form": form,
        "email": request.user.email,
    }
    return render(request, "profile.html", context)





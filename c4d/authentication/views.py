from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .forms import ProfileUpdateForm

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





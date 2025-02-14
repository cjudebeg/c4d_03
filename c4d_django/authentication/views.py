# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            print("Registration form errors:", form.errors)  # Debug print
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            # USERNAME = 'email'
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("profile")
            else:
                form.add_error(None, "Invalid credentials. Please try again.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

@login_required
def profile_view(request):
    return render(request, "profile.html", {})

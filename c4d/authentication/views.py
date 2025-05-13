"""
Views for user authentication, profiles, and job board functionality.
"""

from __future__ import annotations

import random
import string
import time
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from allauth.account.utils import send_email_confirmation
from allauth.account.views import SignupView, PasswordChangeView

# Import basic forms and models that should always be available
from .forms import ProfileUpdateForm, EmailForm, CustomUserSignupForm
from .models import Profile

# Get the User model
User = get_user_model()

# Check if job models and forms are available
try:
    from .models import Job, JobApplication, Rfqt, Message
    from .forms import RfqtForm, JobForm, JobApplicationForm, JobSearchForm, MessageForm
    JOB_MODELS_EXIST = True
except ImportError:
    # Set a flag to disable job-related views
    JOB_MODELS_EXIST = False


def refine_name(name: str) -> str:
    """
    Convert e.g. "dAVE    NaiR" → "Dave Nair".
    Splits on whitespace and capitalizes each part.
    """
    if not name:
        return ""
    parts = name.split()
    return " ".join(part.capitalize() for part in parts)


# --------------------------------------------------------------------------- #
#  Custom signup                                                              #
# --------------------------------------------------------------------------- #

class CustomSignupView(SignupView):
    """Custom signup view using allauth with our form."""
    form_class = CustomUserSignupForm
    template_name = "account/signup.html"

    def form_invalid(self, form):
        """Display form errors as messages."""
        for _field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


# --------------------------------------------------------------------------- #
#  MFA helpers                                                                #
# --------------------------------------------------------------------------- #

@login_required
def mfa_setup(request):
    """
    Step 1 – send OTP to e-mail.
    Initiates the MFA process by generating and emailing an OTP code.
    """
    # Keep any messages except the auto-login one
    for msg in list(messages.get_messages(request)):
        if "successfully signed in" not in msg.message.lower():
            messages.add_message(request, msg.level, msg.message)

    user = request.user
    code = "".join(random.choices(string.digits, k=6))
    now = int(time.time())

    # Store OTP and timing information in session
    request.session["mfa_code"] = code
    request.session["mfa_confirmed"] = False
    request.session["mfa_code_generated_at"] = now
    request.session["mfa_code_expires_at"] = now + 600  # 10 minutes

    # Send OTP via email
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
    """
    Step 2 – verify OTP.
    Validates the OTP entered by the user.
    """
    now = int(time.time())
    
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        code_in_session = request.session.get("mfa_code")
        expires_at = request.session.get("mfa_code_expires_at", 0)

        # Check if OTP has expired
        if now > expires_at:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect("mfa_resend")

        # Validate OTP
        if code_in_session and token == code_in_session:
            request.session["mfa_confirmed"] = True
            # Clean up session
            for key in ("mfa_code", "mfa_code_generated_at", "mfa_code_expires_at"):
                request.session.pop(key, None)
            messages.success(request, "MFA verification successful.")
            return redirect("profile")

        messages.error(request, "Invalid OTP. Please try again.")

    # Prepare resend information
    resend_wait = 0
    otp_resend_available = False
    code_generated = request.session.get("mfa_code_generated_at")

    if code_generated:
        elapsed = now - code_generated
        if elapsed >= 60:  # 1 minute rate limit for resends
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
    """
    Resend OTP (rate-limited to once per minute).
    """
    now = int(time.time())
    generated_at = request.session.get("mfa_code_generated_at", 0)
    
    # Rate limiting check
    if now - generated_at < 60:
        messages.error(request, "You cannot resend OTP until 1 minute has passed.")
        return redirect("mfa_verify")

    # Generate new OTP
    user = request.user
    code = "".join(random.choices(string.digits, k=6))
    request.session["mfa_code"] = code
    request.session["mfa_code_generated_at"] = now
    request.session["mfa_code_expires_at"] = now + 600

    # Send new OTP
    send_mail(
        subject="Your new MFA code",
        message=f"Your new MFA code is: {code}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "mfa@c4defence.com.au"),
        recipient_list=[user.email],
    )
    messages.info(request, "A new OTP has been sent to your registered email address.")
    return redirect("mfa_verify")


# --------------------------------------------------------------------------- #
#  On-boarding and profile                                                    #
# --------------------------------------------------------------------------- #

@login_required
def onboarding_view(request):
    """
    First-time profile wizard.
    Refines first, middle, last names to Title Case before saving.
    """
    # Ensure MFA is completed
    if not request.session.get("mfa_confirmed", False):
        return redirect("mfa_setup")

    # Get or create profile
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user)

    # Skip onboarding if already completed
    if profile.onboarding_completed:
        return redirect("profile")

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        form.fields["clearance_level"].required = False
        if form.is_valid():
            inst = form.save(commit=False)
            # Normalize names to Title Case
            inst.first_name = refine_name(inst.first_name or "")
            inst.middle_name = refine_name(inst.middle_name or "")
            inst.last_name = refine_name(inst.last_name or "")
            inst.onboarding_completed = True
            inst.save()
            return redirect("profile")

        # Display form errors
        for error in form.errors.get("__all__", []):
            messages.error(request, error)
    else:
        form = ProfileUpdateForm(instance=profile)
        form.fields["clearance_level"].required = False

    return render(request, "users/onboarding.html", {
        "form": form,
        "onboarding": True,
        "user": request.user,
    })


@login_required
def profile_view(request, username: str | None = None):
    """
    Display profile for current or arbitrary user.
    """
    # Ensure MFA is completed
    if not request.session.get("mfa_confirmed", False):
        return redirect("mfa_setup")

    # Get profile by username or current user
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except ObjectDoesNotExist:
            return redirect_to_login(request.get_full_path())

    # Redirect to onboarding if not completed
    if not profile.onboarding_completed:
        return redirect("onboarding")

    return render(request, "users/profile.html", {"profile": profile})


# --------------------------------------------------------------------------- #
#  Inline / AJAX helpers                                                      #
# --------------------------------------------------------------------------- #

@login_required
@require_POST
def request_name_change_view(request):
    """
    Capture a user's name-change request (first, middle, last),
    normalize each to Title Case, and reset name_change_done.
    """
    # Verify this is an AJAX request
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return HttpResponseBadRequest("Invalid request")

    # Get name data from form
    raw_first = request.POST.get("new_first", "").strip()
    raw_middle = request.POST.get("new_middle", "").strip()
    raw_last = request.POST.get("new_last", "").strip()
    reason = request.POST.get("reason", "").strip()

    # Validate required fields
    if not raw_first or not raw_last:
        return JsonResponse({
            "success": False,
            "message": "Both first and last names are required."
        })

    # Normalize names
    new_first = refine_name(raw_first)
    new_middle = refine_name(raw_middle)
    new_last = refine_name(raw_last)

    # Update profile
    profile = request.user.profile
    profile.pending_first_name = new_first
    profile.pending_middle_name = new_middle
    profile.pending_last_name = new_last
    profile.pending_name_reason = reason
    profile.pending_name_requested = timezone.now()
    profile.name_change_done = False

    # Save only the changed fields
    profile.save(update_fields=[
        "pending_first_name",
        "pending_middle_name",
        "pending_last_name",
        "pending_name_reason",
        "pending_name_requested",
        "name_change_done",
    ])

    return JsonResponse({
        "success": True,
        "message": "Your name-change request has been submitted."
    })


@login_required
def update_account_view(request):
    """
    Change current e-mail address (triggers verification).
    """
    user = request.user
    if request.method == "POST":
        new_email = request.POST.get("email", "").strip()
        
        # Validate email
        if not new_email:
            messages.error(request, "Email is required.")
            return redirect("profile")

        # Check if email is already in use by current user
        if user.email.lower() == new_email.lower():
            messages.error(request, "This is already your current email address.")
            return redirect("profile")

        from allauth.account.models import EmailAddress

        # Check if email is in use by another user
        if (
            User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists()
            or EmailAddress.objects.filter(email__iexact=new_email).exclude(user=user).exists()
        ):
            messages.error(request, f"{new_email} is already in use by an account.")
            return redirect("profile")

        # Update email and send verification
        EmailAddress.objects.filter(user=user).delete()
        user.email = new_email
        user.save()
        send_email_confirmation(request, user)
        messages.success(request, "Email updated! Verification e-mail sent.")
        return redirect("profile")
    return redirect("profile")


@login_required
def update_personal_view(request):
    """
    Update suburb, state only. Names are admin-only.
    """
    profile = request.user.profile
    if request.method == "POST":
        # Update profile with form data
        profile.suburb = request.POST.get("suburb", profile.suburb)
        state_full = request.POST.get("state", profile.state)
        
        # Map full state names to abbreviations
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
    """
    Users can edit clearance_level only. clearance_valid / active are admin-only.
    """
    profile = request.user.profile
    if request.method == "POST":
        profile.clearance_level = request.POST.get("clearance_level", profile.clearance_level)
        profile.save()
        messages.success(request, "Security clearance information updated.")
        return redirect("profile")
    return redirect("profile")


@login_required
def update_skills_view(request):
    """
    Update selected skills & level.
    """
    profile = request.user.profile
    if request.method == "POST":
        # Process multi-select skills
        chosen_skills = request.POST.getlist("skill_sets_multiple", [])
        profile.skill_sets = ", ".join(chosen_skills)
        profile.skill_level = request.POST.get("skill_level", profile.skill_level)
        profile.save()
        messages.success(request, "Skill information updated.")
        return redirect("profile")
    return redirect("profile")


@login_required
def profile_emailchange(request):
    """
    AJAX endpoint for changing e-mail.
    """
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            
            # Check if email is already in use by current user
            if request.user.email.lower() == email.lower():
                return JsonResponse({"success": False, "message": "This is already your current email address."})

            from allauth.account.models import EmailAddress

            # Check if email is in use by another user
            if (
                User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists()
                or EmailAddress.objects.filter(email__iexact=email).exclude(user=request.user).exists()
            ):
                return JsonResponse({"success": False, "message": f"{email} is already in use by an account."})

            # Update email and send verification
            EmailAddress.objects.filter(user=request.user).delete()
            user = request.user
            user.email = email
            user.save()
            send_email_confirmation(request, user)
            return JsonResponse({"success": True, "message": "Email updated! Verification email sent.", "email": email})

        # Return form error
        error_message = form.errors.get("email", ["Invalid e-mail address."])[0]
        return JsonResponse({"success": False, "message": error_message})
    return redirect("profile")


@login_required
@require_POST
def profile_emailverify(request):
    """
    Trigger verification e-mail.
    """
    send_email_confirmation(request, request.user)
    return JsonResponse({"success": True, "message": "Verification e-mail sent."})


@login_required
def profile_delete_view(request):
    """
    Self-service delete.
    """
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity.")
        return redirect("home")
    return render(request, "users/profile_delete.html")


class CustomPasswordChangeView(PasswordChangeView):
    """
    Force a sign-out after password change and display a success toast
    on the login page.
    """
    template_name = "password_change.html"  # keep your template
    success_url = reverse_lazy("account_login")  # where we want to land

    def form_valid(self, form):
        # 1. Save the new password (does NOT log the user in again)
        form.save()

        # 2. Flush the session
        logout(self.request)

        # 3. Use the cookie-based message store (user is now anonymous)
        messages.success(
            self.request,
            "Your password has been changed successfully. Please sign in again."
        )

        # 4. Go to /accounts/login/
        return redirect(self.get_success_url())

    from django.template.loader import get_template

def home_view(request):
    jobs = Job.objects.filter(is_active=True).order_by('-submission_date')[:3] if JOB_MODELS_EXIST else []

    # <── the only line that matters
    return render(request, "home.html",  # tell Django exactly which template
                  {"showcase_jobs": jobs})



# --------------------------------------------------------------------------- #
#  Job Board Views                                                           #
# --------------------------------------------------------------------------- #

# Only defining job-related views if the models exist
if JOB_MODELS_EXIST:
    @login_required
    def dashboard_view(request):
        """
        Enhanced dashboard view with debugging.
        """
        # Force MFA confirmation
        request.session["mfa_confirmed"] = True
        
        # Get all jobs and print diagnostics
        all_jobs = Job.objects.all()
        jobs_count = all_jobs.count()
        print(f"DASHBOARD DEBUG: Found {jobs_count} jobs in database")
        
        # Print details of each job for verification
        for job in all_jobs:
            print(f"DASHBOARD DEBUG: Job ID: {job.id}, Title: {job.title}, Active: {job.is_active}")
        
        # Handle selected job from URL parameter
        selected_job_id = request.GET.get('selected')
        selected_job = None
        
        if selected_job_id:
            try:
                selected_job = Job.objects.get(id=selected_job_id)
                print(f"DASHBOARD DEBUG: Selected job by URL param: {selected_job.title}")
            except (Job.DoesNotExist, ValueError):
                print(f"DASHBOARD DEBUG: Invalid selected job ID: {selected_job_id}")
                if all_jobs.exists():
                    selected_job = all_jobs.first()
                    print(f"DASHBOARD DEBUG: Defaulting to first job: {selected_job.title}")
        elif all_jobs.exists():
            selected_job = all_jobs.first()
            print(f"DASHBOARD DEBUG: No selection, defaulting to first job: {selected_job.title}")
        else:
            print("DASHBOARD DEBUG: No jobs available for selection")
        
        # Get user applications
        user_applications = JobApplication.objects.filter(user=request.user)
        applications_count = user_applications.count()
        print(f"DASHBOARD DEBUG: User has {applications_count} applications")
        
        # Create context with explicit debugging
        context = {
            'all_jobs': all_jobs,
            'selected_job': selected_job,
            'user_applications': user_applications,
            'jobs_count': jobs_count,  # Add this for template debugging
            'debug_info': f"Found {jobs_count} jobs, Selected job: {selected_job.title if selected_job else 'None'}"
        }
        
        # Identify which template is being used
        print(f"DASHBOARD DEBUG: Rendering template: dashboard.html")
        
        # Try a completely different approach - directly create a list for template rendering
        return render(request, "dashboard.html", context)


    @login_required
    def job_list_view(request):
        """
        List view of all active jobs with filtering.
        Traditional paginated list of jobs.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Get active jobs
        jobs = Job.objects.filter(is_active=True)
        
        # Process search/filtering
        form = JobSearchForm(request.GET)
        if form.is_valid():
            job_type = form.cleaned_data.get('job_type')
            location = form.cleaned_data.get('location')
            clearance = form.cleaned_data.get('clearance')
            keyword = form.cleaned_data.get('keyword')
            
            # Apply filters if provided
            if job_type:
                jobs = jobs.filter(job_type=job_type)
            if location:
                jobs = jobs.filter(location=location)
            if clearance:
                jobs = jobs.filter(clearance=clearance)
            if keyword:
                jobs = jobs.filter(
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(short_description__icontains=keyword) |
                    Q(skills_sets__icontains=keyword)
                )
        
        # Paginate results
        paginator = Paginator(jobs, 10)  # Show 10 jobs per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique filter options
        job_types = Job.objects.values_list('job_type', flat=True).distinct()
        locations = Job.objects.values_list('location', flat=True).distinct()
        clearances = Job.objects.values_list('clearance', flat=True).distinct()
        
        context = {
            'page_obj': page_obj,
            'search_form': form,
            'job_types': job_types,
            'locations': locations,
            'clearances': clearances,
        }
        
        return render(request, "job_list.html", context)


    @login_required
    def job_detail_view(request, job_id):
        """
        Detailed view of a specific job.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Get job or 404
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        # Check if user has already applied
        has_applied = JobApplication.objects.filter(job=job, user=request.user).exists()
        
        # Get related messages if staff
        messages_list = None
        if request.user.is_staff:
            messages_list = Message.objects.filter(job=job).order_by('timestamp')
        
        context = {
            'job': job,
            'has_applied': has_applied,
            'messages': messages_list,
        }
        
        return render(request, "job_detail.html", context)


    @login_required
    def job_apply_view(request, job_id):
        """
        Apply for job.
        """

        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Get job or 404
        job = get_object_or_404(Job, id=job_id, is_active=True)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, user=request.user).exists():
            messages.warning(request, "You have already applied for this job.")
            return redirect('job_detail', job_id=job.id)
        
        if request.method == 'POST':
            form = JobApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                # Save application
                application = form.save(commit=False)
                application.job = job
                application.user = request.user
                application.rfqts_no = job.rfqts_no
                application.save()
                
                # Send message to admin if provided
                if request.POST.get('message_content'):
                    recipient = User.objects.filter(is_superuser=True).first()
                    if recipient:
                        Message.objects.create(
                            sender=request.user,
                            recipient=recipient,
                            job=job,
                            application=application,
                            content=request.POST.get('message_content')
                        )
                
                messages.success(request, "Your application has been submitted successfully!")
                return redirect('job_application_success')
        else:
            # Pre-fill form with user profile data
            initial_data = {}
            try:
                profile = request.user.profile
                if profile.first_name and profile.last_name:
                    initial_data['full_name'] = f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip()
                if profile.clearance_level:
                    initial_data['current_clearance'] = profile.clearance_level
                if profile.clearance_revalidation:
                    initial_data['clearance_expiry_date'] = profile.clearance_revalidation
                if profile.clearance_no:
                    initial_data['clearance_number'] = profile.clearance_no
                if profile.suburb and profile.state:
                    initial_data['location_of_residence'] = f"{profile.suburb}, {profile.state}"
                if profile.date_of_birth:
                    initial_data['date_of_birth'] = profile.date_of_birth
            except ObjectDoesNotExist:
                pass
            
            form = JobApplicationForm(initial=initial_data)
        
        context = {
            'form': form,
            'job': job,
            'message_form': MessageForm(),
        }
        
        return render(request, "job_apply.html", context)


    @login_required
    def job_application_success(request):
        """
        Success page after job application submission.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        return render(request, "job_application_success.html")


    @login_required
    def my_applications_view(request):
        """
        View all applications by the current user.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Get user applications
        applications = JobApplication.objects.filter(user=request.user).order_by('-submission_date')
        
        context = {
            'applications': applications
        }
        
        return render(request, "my_applications.html", context)


    @login_required
    def application_detail_view(request, application_id):
        """
        View details of a specific application with messaging.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Get application or 404
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Security check - only owner or staff can view
        if application.user != request.user and not request.user.is_staff:
            messages.error(request, "You do not have permission to view this application.")
            return redirect('job_list')
        
        # Get related messages
        application_messages = Message.objects.filter(application=application).order_by('timestamp')
        
        # Handle new message submission
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.application = application
                message.job = application.job
                
                # Set recipient - if staff, send to applicant, otherwise send to staff
                if request.user.is_staff:
                    message.recipient = application.user
                else:
                    message.recipient = User.objects.filter(is_staff=True).first()
                
                message.save()
                messages.success(request, "Message sent successfully.")
                return redirect('application_detail', application_id=application.id)
        else:
            form = MessageForm()
        
        context = {
            'application': application,
            'messages': application_messages,
            'message_form': form,
        }
        
        return render(request, "application_detail.html", context)


    @login_required
    def mark_message_as_read(request, message_id):
        """
        Mark a message as read.
        """
        # Only the recipient can mark a message as read
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.is_read = True
        message.save()
        
        return JsonResponse({'success': True})


    # --------------------------------------------------------------------------- #
    #  Admin Job Views                                                           #
    # --------------------------------------------------------------------------- #

    @login_required
    def admin_job_list(request):
        """
        Admin view for managing all jobs.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Check permissions
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        # Get all jobs
        jobs = Job.objects.all().order_by('-submission_date')
        
        context = {
            'jobs': jobs
        }
        
        return render(request, "admin/job_list.html", context)


    @login_required
    def admin_job_create(request):
        """
        Admin view for creating a new job.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Check permissions
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        if request.method == 'POST':
            form = JobForm(request.POST)
            if form.is_valid():
                job = form.save()
                messages.success(request, f"Job '{job.title}' created successfully.")
                return redirect('admin_job_list')
        else:
            form = JobForm()
        
        context = {
            'form': form,
            'title': 'Create New Job'
        }
        
        return render(request, "admin/job_form.html", context)


    @login_required
    def admin_job_edit(request, job_id):
        """
        Admin view for editing an existing job.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Check permissions
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        # Get job or 404
        job = get_object_or_404(Job, id=job_id)
        
        if request.method == 'POST':
            form = JobForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, f"Job '{job.title}' updated successfully.")
                return redirect('admin_job_list')
        else:
            form = JobForm(instance=job)
        
        context = {
            'form': form,
            'job': job,
            'title': 'Edit Job'
        }
        
        return render(request, "admin/job_form.html", context)


    @login_required
    def admin_job_delete(request, job_id):
        """
        Admin view for deleting a job.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Check permissions
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        # Get job or 404
        job = get_object_or_404(Job, id=job_id)
        
        if request.method == 'POST':
            job_title = job.title
            job.delete()
            messages.success(request, f"Job '{job_title}' deleted successfully.")
            return redirect('admin_job_list')
        
        context = {
            'job': job
        }
        
        return render(request, "admin/job_confirm_delete.html", context)


    @login_required
    def admin_applications(request):
        """
        Admin view for managing all job applications.
        """
        # Ensure MFA is completed
        if not request.session.get("mfa_confirmed", False):
            return redirect("mfa_setup")
        
        # Check permissions
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        # Get all applications
        applications = JobApplication.objects.all().order_by('-submission_date')
        
        # Handle filtering
        job_id = request.GET.get('job')
        status = request.GET.get('status')
        
        if job_id:
            applications = applications.filter(job_id=job_id)
        if status:
            applications = applications.filter(status=status)
        
        context = {
            'applications': applications,
            'jobs': Job.objects.all(),
            'statuses': JobApplication._meta.get_field('status').choices,
            'selected_job': job_id,
            'selected_status': status,
        }
        
        return render(request, "admin/applications_list.html", context)


    @login_required
    @require_POST
    def admin_update_application_status(request, application_id):
        """
        Admin endpoint for updating application status.
        """
        # Check permissions
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        application = get_object_or_404(JobApplication, id=application_id)
        
        status = request.POST.get('status')
        valid_statuses = dict(JobApplication._meta.get_field('status').choices)
        
        # Update status if valid
        if status in valid_statuses:
            application.status = status
            application.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)

else:
    # Provide fallback views when job models don't exist
    @login_required
    def dashboard_view(request):
        """Fallback dashboard when job models aren't available."""
        return render(request, "dashboard_fallback.html")

    def job_list_view(request):
        return redirect("home")

    def job_detail_view(request, job_id):
        return redirect("home")

    def job_apply_view(request, job_id):
        return redirect("home")

    def job_application_success(request):
        return redirect("home")

    def my_applications_view(request):
        return redirect("profile")

    def application_detail_view(request, application_id):
        return redirect("profile")

    def mark_message_as_read(request, message_id):
        return JsonResponse({'success': False, 'message': 'Feature not available'})

    def admin_job_list(request):
        return redirect("home")

    def admin_job_create(request):
        return redirect("home")

    def admin_job_edit(request, job_id):
        return redirect("home")

    def admin_job_delete(request, job_id):
        return redirect("home")

    def admin_applications(request):
        return redirect("home")

    def admin_update_application_status(request, application_id):
        return JsonResponse({'success': False, 'message': 'Feature not available'})
from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import SignupForm, AddEmailForm as AllauthAddEmailForm
from django.utils.translation import gettext as _
from allauth.account.models import EmailAddress
from .models import Profile, STATE_CHOICES, CLEARANCE_LEVEL_CHOICES

User = get_user_model()

class AddEmailForm(AllauthAddEmailForm):
    # For Adding emails in add email section
    # Custom add email form that checks if the email is already in use in the EmailAddress table

    def clean_email(self):
        email = super().clean_email()
        if not email:
            return email
         # Prevention of user account creation with local parts like root, admin, or sa
        local_part = email.split('@')[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email local part is not allowed."))
        # This checks if this email is already associated with any account
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("That email is already in use. Please sign in or choose another.")
            )
        return email

class CustomUserSignupForm(SignupForm):
    # Custom signup form with Allauth integration for new user registration

    def clean_email(self):
        email = super().clean_email()
        if not email:
            return email
        local_part = email.split('@')[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email local part is not allowed."))
        # Check in User model
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("That email is already in use, please sign in or use a different one.")
            )
        # Also check in the EmailAddress table
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("That email is already in use, please sign in or use a different one.")
            )
        return email

    def save(self, request):
        # Save the user using Allauth and return the user instance
        user = super().save(request)
        return user

class CustomUserChangeForm(UserChangeForm):
    # Form for users to update their profile information.
    class Meta:
        model = User
        fields = '__all__'

class ProfileUpdateForm(ModelForm):

    skill_sets = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search or enter your skills"}),
        label="Skill Type (Search)"
    )
    skill_level = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select skill level"),
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        label="Skill Level"
    )

    class Meta:
        model = Profile
        fields = [
            "first_name", "middle_name", "last_name", "date_of_birth",
            "state", "suburb", "clearance_level", "clearance_no",
            "clearance_revalidation", "clearance_active", "skill_sets", "skill_level"
        ]
        widgets = {
            "state": forms.Select(choices=STATE_CHOICES, attrs={"placeholder": "Select State/Territory"}),
            "suburb": forms.TextInput(attrs={"placeholder": "Your Suburb"}),
            "date_of_birth": forms.DateInput(attrs={'type': 'date', 'placeholder': 'In DD/MM/YYYY format'}),
            "clearance_level": forms.Select(choices=CLEARANCE_LEVEL_CHOICES, attrs={"placeholder": "Select your Clearance Level"}),
            "clearance_no": forms.TextInput(attrs={"placeholder": "Enter CSID number"}),
            "clearance_revalidation": forms.DateInput(attrs={'type': 'date', 'placeholder': 'Revalidation Date'}),
            "clearance_active": forms.CheckboxInput(),
        }
        labels = {
            "state": "Your Location",
            "date_of_birth": "Date of Birth",
            "clearance_level": "Your AGVSA security clearance",
            "clearance_no": "CSID Number",
            "clearance_revalidation": "Clearance Revalidation",
            "clearance_active": "Clearance Active",
        }
        help_texts = {
            "state": "Select state/territory (optional).",
            "clearance_level": "Select from the list (optional).",
            "clearance_no": "CSID number (auto-prefix 'CS').",
        }

    def __init__(self, *args, **kwargs):
        # Initialise the form and update fields
        # Optional keyword arg 'admin_edit' (default False): if not True, then clearance_revalidation
        # and clearance_active are disabled.
        admin_edit = kwargs.pop('admin_edit', False)
        super().__init__(*args, **kwargs)
        self.fields["state"].required = False
        self.fields["suburb"].required = False
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["clearance_level"].required = True

        original_state_choices = list(self.fields["state"].choices)
        self.fields["state"].choices = [("", "Select State/Territory")] + original_state_choices[1:]
        original_clearance_choices = list(self.fields["clearance_level"].choices)
        self.fields["clearance_level"].choices = [("", "Select Clearance Level")] + original_clearance_choices[1:]
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (
                existing_classes +
                " block w-full bg-gray-100 px-2 py-2 mb-4 border border-gray-300 " +
                "focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            ).strip()
        # Only allow admin to modify clearance_revalidation and clearance_active.
        if not admin_edit:
            if 'clearance_revalidation' in self.fields:
                self.fields['clearance_revalidation'].widget.attrs['disabled'] = True
            if 'clearance_active' in self.fields:
                self.fields['clearance_active'].widget.attrs['disabled'] = True

    def clean_clearance_no(self):
        # Validate the clearance number ensuring it has the correct prefix and numeric part
        clearance_no = self.cleaned_data.get("clearance_no")
        if clearance_no:
            if not clearance_no.startswith("CS"):
                clearance_no = "CS" + clearance_no
            numeric_part = clearance_no[2:]
            if not numeric_part.isdigit():
                raise forms.ValidationError("The CSID number must contain only digits after 'CS'.")
            if not (2 <= len(numeric_part) <= 25):
                raise forms.ValidationError("CSID numeric part must be 2-25 digits.")
            self.cleaned_data["clearance_no"] = clearance_no
        return clearance_no

    def clean(self):
        # Validate that either Date of Birth or Clearance Number is provided
        cleaned_data = super().clean()
        dob = cleaned_data.get("date_of_birth")
        clearance_no = cleaned_data.get("clearance_no")
        if not dob and not clearance_no:
            raise forms.ValidationError("Please enter either your valid Clearance Number or Date of Birth.")
        return cleaned_data

class EmailForm(forms.Form):
    # Form for updating the user's email address with duplicate-checking
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded w-full',
            'placeholder': 'Enter new email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        local_part = email.split('@')[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email address is not allowed."))
        return email

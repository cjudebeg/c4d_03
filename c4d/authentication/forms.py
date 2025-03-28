from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import SignupForm
from .models import Profile, STATE_CHOICES, CLEARANCE_LEVEL_CHOICES
import re
from django.utils.translation import gettext as _
from allauth.account.models import EmailAddress
from allauth.account.forms import AddEmailForm as AllauthAddEmailForm

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override help text and set id attributes for password and email fields
        self.fields['password1'].help_text = ()
        self.fields['password1'].widget.attrs.update({"id": "id_password1"})
        self.fields['password2'].widget.attrs.update({"id": "id_password2"})
        self.fields['email'].widget.attrs.update({"id": "id_email"})

    def clean_email(self):
        # Prevention of user account creation with local parts like root, admin, or sa
        email = super().clean_email()
        local_part = email.split('@')[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email local part is not allowed."))
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("That email is already in use, please sign in or use a different one.")
            )
        return email

    def save(self, request):
        # Save the user using Allauth and return the user instance
        user = super().save(request)
        return user


class CustomUserChangeForm(UserChangeForm):
    # Form for users to update their profile information
    pass


class ProfileUpdateForm(ModelForm):
    # Merged Profile Update Form combining fields from ProfileForm and existing ProfileUpdateForm

    skill_sets = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Search or enter your skills"}
        ),
        label="Skill Type (Search)",
    )
    skill_level = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select Skill Level"),
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        label="Skill Level",
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "date_of_birth",
            "state",
            "suburb",
            "clearance_level",
            "clearance_no",  # CSID number
            "clearance_expiry",
            "skill_sets",
            "skill_level",
        ]
        widgets = {
            "state": forms.Select(
                choices=STATE_CHOICES,
                attrs={"placeholder": "Select State/Territory"},
            ),
            "suburb": forms.TextInput(
                attrs={"placeholder": "Your Suburb"},
            ),
            "date_of_birth": forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'In DD/MM/YYYY format'},
            ),
            "clearance_level": forms.Select(
                choices=CLEARANCE_LEVEL_CHOICES,
                attrs={"placeholder": "Select your Clearance Level"},
            ),
            "clearance_no": forms.TextInput(
                attrs={"placeholder": "Your CSID number"},
            ),
            "clearance_expiry": forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'Expiry Date'},
            ),
        }
        labels = {
            "state": "Your Location",
            "date_of_birth": "Date of Birth",
            "clearance_level": "Your AGVSA security clearance",
            "clearance_no": "CSID Number",
            "clearance_expiry": "Expiry Date",
        }
        help_texts = {
            "state": "Select state/territory (optional).",
            "clearance_level": "Select from the list (optional).",
            "clearance_no": "CSID number (auto-prefix 'CS').",
        }

    def __init__(self, *args, **kwargs):
        # Initialise the form and update fields
        super().__init__(*args, **kwargs)
        self.fields["state"].required = False
        self.fields["suburb"].required = False

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["clearance_level"].required = True

        # Replace the dropdown default "---------" value with a placeholder
        original_state_choices = list(self.fields["state"].choices)
        self.fields["state"].choices = [("", "Select State/Territory")] + original_state_choices[1:]
        original_clearance_choices = list(self.fields["clearance_level"].choices)
        self.fields["clearance_level"].choices = [("", "Select Clearance Level")] + original_clearance_choices[1:]
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (
                existing_classes +
                " block w-full bg-gray-100 px-2 py-2 mb-4 border border-gray-300 "
                "focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            ).strip()

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
            raise forms.ValidationError(
                "Please enter either your Date of Birth or a Clearance Number."
            )
        return cleaned_data


class EmailForm(forms.Form):
    # Form for updating the user's email address with duplicate-checking
    email = forms.EmailField(required=False)

    def clean_email(self):
        # Ensure that the provided email is not already associated with any account
        email = self.cleaned_data.get("email")
        if email:
            if EmailAddress.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError(
                    _("That email is already in use — please sign in or choose another.")
                )
        return email

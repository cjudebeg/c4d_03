from datetime import date
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
    # For adding emails in “Add email” section
    # Prevents duplicates and disallowed local parts
    def clean_email(self):
        email = super().clean_email()
        if not email:
            return email
        local_part = email.split("@")[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email local part is not allowed."))
        if EmailAddress.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("That email is already in use. Please sign in or choose another.")
            )
        return email


class CustomUserSignupForm(SignupForm):
    # Custom signup form with Allauth integration
    def clean_email(self):
        email = super().clean_email()
        if not email:
            return email
        local_part = email.split("@")[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email local part is not allowed."))
        if (User.objects.filter(email__iexact=email).exists() or
            EmailAddress.objects.filter(email__iexact=email).exists()):
            raise forms.ValidationError(
                _("That email is already in use, please sign in or use a different one.")
            )
        return email

    def save(self, request):
        user = super().save(request)
        return user


class CustomUserChangeForm(UserChangeForm):
    # Allows admin to update user fields
    class Meta:
        model = User
        fields = "__all__"


class ProfileUpdateForm(ModelForm):
    # skills field only
    skill_sets = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search or enter your skills"}),
        label="Skill Type (Search)",
    )

    # revalidation date as DD/MM/YYYY
    clearance_revalidation = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "DD/MM/YYYY",
                # Tailwind classes to match the rest
                "class": (
                    "block w-full bg-gray-100 px-2 py-2 mb-4 "
                    "border border-gray-300 focus:outline-none "
                    "focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
                ),
            },
        ),
        input_formats=["%d/%m/%Y"],
        label="Clearance Revalidation",
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
            "clearance_no",
            "clearance_revalidation",
            "clearance_active",
            "skill_sets",
        ]
        widgets = {
            "state": forms.Select(
                choices=STATE_CHOICES,
                attrs={"placeholder": "Select State/Territory"}
            ),
            "suburb": forms.TextInput(attrs={"placeholder": "Your Suburb"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "placeholder": "In DD/MM/YYYY format"}
            ),
            "clearance_level": forms.Select(
                choices=CLEARANCE_LEVEL_CHOICES,
                attrs={"placeholder": "Select your Clearance Level"}
            ),
            "clearance_no": forms.TextInput(attrs={"placeholder": "Enter CSID number"}),
            "clearance_active": forms.CheckboxInput(),
        }
        labels = {
            "state": "Your Location",
            "date_of_birth": "Date of Birth",
            "clearance_level": "Your AGSVA security clearance",
            "clearance_no": "CSID Number",
            "clearance_active": "Clearance Active",
        }
        help_texts = {
            "state": "Select state/territory (optional).",
            "clearance_level": "Select from the list (optional).",
            "clearance_no": "CSID number (auto-prefix 'CS').",
        }

    # ─────────────────────────────── INIT ───────────────────────────────
    def __init__(self, *args, **kwargs):
        admin_edit = kwargs.pop("admin_edit", False)
        super().__init__(*args, **kwargs)

        # Mark required fields
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["clearance_level"].required = True

        self.fields["state"].required = False
        self.fields["suburb"].required = False

        # Prepend placeholders to selects
        self.fields["state"].choices = [("", "Select State/Territory")] + list(self.fields["state"].choices)[1:]
        self.fields["clearance_level"].choices = [("", "Select Clearance Level")] + list(
            self.fields["clearance_level"].choices
        )[1:]

        # Override invalid-choice message
        self.fields["clearance_level"].error_messages = {
            "invalid_choice": "Select your clearance level"
        }

        # Tailwind styling for all other widgets
        for name, field in self.fields.items():
            if name != "clearance_revalidation":
                extra = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (
                    f"{extra} block w-full bg-gray-100 px-2 py-2 mb-4 "
                    "border border-gray-300 focus:outline-none "
                    "focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
                ).strip()

        # Lock certain fields for normal users
        if not admin_edit:
            for lock in ("clearance_revalidation", "clearance_active"):
                if lock in self.fields:
                    self.fields[lock].widget.attrs["disabled"] = True

    # ──────────────────── FIELD-LEVEL VALIDATION ────────────────────
    def clean_clearance_no(self):
        raw = self.cleaned_data.get("clearance_no", "").strip()

        if raw:
            # Case-insensitive check for existing "CS" prefix
            if raw[:2].lower() == "cs":
                numeric_part = raw[2:]
            else:
                numeric_part = raw

            # Must be all digits, length 2–25
            if not numeric_part.isdigit():
                raise forms.ValidationError(
                    "The CSID number must contain only digits after 'CS'."
                )
            if not (2 <= len(numeric_part) <= 25):
                raise forms.ValidationError(
                    "CSID numeric part must be between 2 and 25 digits."
                )

            # Normalize to uppercase "CS" + digits
            normalized = f"CS{numeric_part}"

            # Uniqueness check (case-insensitive)
            qs = Profile.objects.filter(
                clearance_no__iexact=normalized
            ).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    "This CSID number is already associated with another profile."
                )

            self.cleaned_data["clearance_no"] = normalized
            return normalized

        return raw

    # ─────────────────────── FORM-WIDE VALIDATION ───────────────────────
    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get("date_of_birth")
        clearance_no = cleaned_data.get("clearance_no")

        # Must supply either DOB or CSID
        if not dob and not clearance_no:
            raise forms.ValidationError(
                "Please enter either your valid Clearance Number or Date of Birth."
            )

        # Enforce minimum age 16
        if dob:
            today = date.today()
            age_years = (today - dob).days // 365
            if age_years < 16:
                raise forms.ValidationError(
                    "Registrants must be at least 16 years old."
                )

        return cleaned_data


class EmailForm(forms.Form):
    # Form for updating the user's email address with duplicate-checking
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "px-3 py-2 border border-gray-300 rounded w-full",
                "placeholder": "Enter new email address",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        local_part = email.split("@")[0].lower()
        if local_part in ["root", "admin", "sa"]:
            raise forms.ValidationError(_("This email address is not allowed."))
        return email

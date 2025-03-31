from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import SignupForm
from .models import Profile, STATE_CHOICES, CLEARANCE_LEVEL_CHOICES
import re
from django.utils.translation import gettext as _

User = get_user_model()


class CustomUserSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override helptext to remove the different from your current password msg (to fix multiple space validator issue)
        self.fields["password1"].help_text = ()
        # Ensure password and email fields have the correct id attributes
        self.fields["password1"].widget.attrs.update({"id": "id_password1"})
        self.fields["password2"].widget.attrs.update({"id": "id_password2"})
        self.fields["email"].widget.attrs.update({"id": "id_email"})

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1:
            new_password = re.sub(r"\s{2,}", " ", password1)
            if new_password != password1:
                cleaned_data["password1"] = new_password
                cleaned_data["password2"] = new_password
                self.password_modified = True
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        if getattr(self, "password_modified", False):
            from django.contrib import messages

            messages.info(
                request,
                _(
                    "Your password was modified: consecutive spaces have been replaced with a single space."
                ),
            )
        return user


class CustomUserChangeForm(UserChangeForm):

    pass


# Merged Profile Update Form combining fields from ProfileForm and existing ProfileUpdateForm.
class ProfileUpdateForm(ModelForm):
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
            # Extra fields
            "skill_sets",
            "skill_level",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "placeholder": "DD/MM/YYYY"}
            ),
            "clearance_expiry": forms.DateInput(
                attrs={"type": "date", "placeholder": "Expiry DD/MM/YYYY"}
            ),
            "suburb": forms.TextInput(attrs={"placeholder": "Your Suburb"}),
            "state": forms.Select(
                choices=STATE_CHOICES, attrs={"placeholder": "Add State/Territory"}
            ),
            "clearance_level": forms.Select(
                choices=CLEARANCE_LEVEL_CHOICES,
                attrs={"placeholder": "Add AGVSA clearance level"},
            ),
            "clearance_no": forms.TextInput(attrs={"placeholder": "Your CSID number"}),
        }
        labels = {
            "date_of_birth": "Date of Birth",
            "state": "State or Territory",
            "clearance_level": "AGVSA security clearance level",
            "clearance_no": "CSID Number",
            "clearance_expiry": "Re-validation Date",
        }
        help_texts = {
            "state": "Select state/territory.",
            "clearance_level": "Select from the list",
            "clearance_no": "CSID number (auto-prefix 'CS')",
        }

    def __init__(self, *args, **kwargs):
        # Initialise the form and update fields
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["clearance_level"].required = True

        self.fields["date_of_birth"].input_formats = ["%d/%m/%Y", "%Y-%m-%d"]

        self.fields["first_name"].widget.attrs.update(
            {"placeholder": "Enter first name"}
        )
        self.fields["middle_name"].widget.attrs.update(
            {"placeholder": "Enter middle name"}
        )
        self.fields["last_name"].widget.attrs.update({"placeholder": "Enter last name"})
        self.fields["date_of_birth"].widget.attrs.update(
            {"placeholder": "In DD/MM/YYYY format"}
        )
        self.fields["suburb"].widget.attrs.update({"placeholder": "Suburb"})
        self.fields["clearance_no"].widget.attrs.update({"placeholder": "CSID number"})

        # Replace the dropdown default "---------" value with placeholder
        original_state_choices = list(self.fields["state"].choices)
        self.fields["state"].choices = [
            ("", "Select State/Territory")
        ] + original_state_choices[1:]

        original_clearance_choices = list(self.fields["clearance_level"].choices)
        self.fields["clearance_level"].choices = [
            ("", "Select Clearance Level")
        ] + original_clearance_choices[1:]

        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (
                existing_classes
                + " block w-full bg-gray-100 px-2 py-2 mb-4 border border-gray-300 "
                "focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            ).strip()

    def clean_clearance_no(self):
        clearance_no = self.cleaned_data.get("clearance_no")
        if clearance_no:
            if not clearance_no.startswith("CS"):
                clearance_no = "CS" + clearance_no
            numeric_part = clearance_no[2:]
            if not numeric_part.isdigit():
                raise forms.ValidationError(
                    "The CSID number must contain only digits after 'CS'."
                )
            # Ensure the numeric part is between 5 and 20 digits.
            if not (5 <= len(numeric_part) <= 20):
                raise forms.ValidationError(
                    "The numeric part must be between 5 and 20 digits."
                )
        return clearance_no

    def clean(self):
        # Check either location or clearance details are provided.
        cleaned_data = super().clean()
        dob = cleaned_data.get("date_of_birth")
        state = cleaned_data.get("state")
        suburb = cleaned_data.get("suburb")
        clearance_level = cleaned_data.get("clearance_level")
        clearance_no = cleaned_data.get("clearance_no")
        clearance_expiry = cleaned_data.get("clearance_expiry")

        location_complete = dob and state and suburb
        clearance_complete = clearance_level and clearance_no and clearance_expiry

        if not (location_complete or clearance_complete):
            raise forms.ValidationError(
                "You must complete either your location details (Date of Birth, State, Suburb) "
                "or your AGVSA security clearance details (Clearance Level, CSID Number, Expiry Date)."
            )
        return cleaned_data


class EmailForm(ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from allauth.account.forms import SignupForm
from .models import Profile

User = get_user_model()

class CustomUserSignupForm(SignupForm):
    # class Meta:
    #     model = get_user_model()
    #     fields = ("email", "username")
    
    # Custom signup form with Allauth, inc profile fields and passwords

    # first_name = forms.CharField(required=True)
    # middle_name = forms.CharField(required=False)
    # last_name = forms.CharField(required=True)
    # date_of_birth = forms.DateField(required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    # agvsa_clearance_number = forms.CharField(label="AGVSA clearance number", required=False)
    # security_clearance = forms.ChoiceField(
    #     choices=[
    #         ('None', 'None'),
    #         ('Pending', 'Pending'),
    #         ('Baseline', 'Baseline'),
    #         ('Negative Vetting 1', 'Negative Vetting 1'),
    #         ('Negative Vetting 2', 'Negative Vetting 2'),
    #         ('Positive Vetting', 'Positive Vetting')
    #     ],
    #     required=True
    # )
    # suburb = forms.CharField(required=False)

    # password1 = forms.CharField(
    #     label="Password",
    #     widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
    #     required=True,
    # )
    # password2 = forms.CharField(
    #     label="Confirm Password",
    #     widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    #     required=True,
    # )

    # def clean_email(self):
    #     """Ensure email is unique."""
    #     email = self.cleaned_data.get("email")
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("This email is already registered.")
    #     return email

    # def clean(self):
    #     Ensure passwords match

    #     cleaned_data = super().clean()
    #     password1 = cleaned_data.get("password1")
    #     password2 = cleaned_data.get("password2")

    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Passwords do not match.")

    #     return cleaned_data

    # def save(self, request):

    #     save user with password and profile fields.

    #     user = super().save(request)  # Save user using Allauth
    #     user.set_password(self.cleaned_data["password1"])  # Hashing pwd
    #     user.save()

    #     profile = user.profile  =
    #     profile.first_name = self.cleaned_data.get("first_name", "")
    #     profile.middle_name = self.cleaned_data.get("middle_name", "")
    #     profile.last_name = self.cleaned_data.get("last_name", "")
    #     profile.date_of_birth = self.cleaned_data.get("date_of_birth", None)
    #     profile.agvsa_clearance_number = self.cleaned_data.get("agvsa_clearance_number", "")
    #     profile.security_clearance = self.cleaned_data.get("security_clearance", "None")
    #     profile.suburb = self.cleaned_data.get("suburb", "")
    #     profile.save()  

    #     return user

    pass

class CustomUserChangeForm(UserChangeForm):
    # class Meta:
    #     model = get_user_model()
    #     fields = ("email", "username")

    # Form for users to update their profile

    # first_name = forms.CharField(required=True)
    # middle_name = forms.CharField(required=False)
    # last_name = forms.CharField(required=True)
    # date_of_birth = forms.DateField(required=True, widget=forms.TextInput(attrs={'type': 'date'}))
    # agvsa_clearance_number = forms.CharField(required=False)
    # security_clearance = forms.ChoiceField(
    #     choices=[
    #         ('None', 'None'),
    #         ('Pending', 'Pending'),
    #         ('Baseline', 'Baseline'),
    #         ('Negative Vetting 1', 'Negative Vetting 1'),
    #         ('Negative Vetting 2', 'Negative Vetting 2'),
    #         ('Positive Vetting', 'Positive Vetting')
    #     ],
    #     required=True
    # )
    # suburb = forms.CharField(required=False)

    # class Meta:
    #     model = User  # This form is still for User but updates Profile too
    #     fields = ("email",)

    # def save(self, commit=True):
    #     
    #     user = super().save(commit=False)
    #     if commit:
    #         user.save()
    #         # Update related Profile fields
    #         profile, created = Profile.objects.get_or_create(user=user)
    #         profile.first_name = self.cleaned_data.get("first_name", "")
    #         profile.middle_name = self.cleaned_data.get("middle_name", "")
    #         profile.last_name = self.cleaned_data.get("last_name", "")
    #         profile.date_of_birth = self.cleaned_data.get("date_of_birth", None)
    #         profile.agvsa_clearance_number = self.cleaned_data.get("agvsa_clearance_number", "")
    #         profile.security_clearance = self.cleaned_data.get("security_clearance", "None")
    #         profile.suburb = self.cleaned_data.get("suburb", "")
    #         profile.save()
    #     return user

    pass
    

# class LoginForm(forms.Form):

#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
#         required=True,
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
#         required=True,
#     )


class ProfileUpdateForm(forms.ModelForm):
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
            "clearance_expiry",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={'type': 'date', 'placeholder': 'DD/MM/YYYY'}),
            "clearance_expiry": forms.DateInput(attrs={'type': 'date', 'placeholder': 'Expiry DD/MM/YYYY'}),
        }
        labels = {
            "date_of_birth": "Date of Birth",
            "state": "Your Location",
            "clearance_level": "Your AGVSA security clearance",
            "clearance_no": "CSID Number",
            "clearance_expiry": "Expiry Date",
        }
        help_texts = {
            "state": "Select state/territory.",
            "clearance_level": "Select from the list",
            "clearance_no": "CSID number (auto-prefix 'CS')",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["clearance_level"].required = True
        
        # Set input formats for dob
        self.fields["date_of_birth"].input_formats = ['%d/%m/%Y', '%Y-%m-%d']
        
        # Placeholder for state nd clearance_level
        original_state_choices = list(self.fields["state"].choices)
        self.fields["state"].choices = [('', 'Select State/Territory')] + original_state_choices
        
        original_clearance_choices = list(self.fields["clearance_level"].choices)
        self.fields["clearance_level"].choices = [('', 'Select from the list')] + original_clearance_choices
        
        self.fields["first_name"].widget.attrs.update({"placeholder": "First Name"})
        self.fields["last_name"].widget.attrs.update({"placeholder": "Last Name"})
        self.fields["date_of_birth"].widget.attrs.update({"placeholder": "DD/MM/YYYY"})
        self.fields["suburb"].widget.attrs.update({"placeholder": "State/Territory, Suburb"})
        self.fields["clearance_no"].widget.attrs.update({"placeholder": "CSID number"})
    
    def clean_clearance_no(self):
        clearance_no = self.cleaned_data.get("clearance_no")
        if clearance_no:
            # Ensuring the value starts with CS
            if not clearance_no.startswith("CS"):
                clearance_no = "CS" + clearance_no
            numeric_part = clearance_no[2:]
            if not numeric_part.isdigit():
                raise forms.ValidationError("The CSID number must contain only digits after 'CS'.")
            if not (5 <= len(numeric_part) <= 20):
                raise forms.ValidationError("The numeric part must be between 5 and 20 digits.")
        return clearance_no

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get("date_of_birth")
        state = cleaned_data.get("state")
        suburb = cleaned_data.get("suburb")
        clearance_level = cleaned_data.get("clearance_level")
        clearance_no = cleaned_data.get("clearance_no")
        clearance_expiry = cleaned_data.get("clearance_expiry")

        # Either complete location details (dob, state, sub) or complete clearance details (clearance_level, clearance_no, clearance_expiry) is required
        location_complete = dob and state and suburb
        clearance_complete = clearance_level and clearance_no and clearance_expiry

        if not (location_complete or clearance_complete):
            raise forms.ValidationError(
                "You must complete either your location details (Date of Birth, State, Suburb) "
                "or your AGVSA security clearance details (Clearance Level, CSID Number, Expiry Date)."
            )
        return cleaned_data

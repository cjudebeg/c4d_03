from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    date_of_birth = forms.DateField(required=True)
    agvsa_clearance_number = forms.CharField(required=False)
    security_clearance = forms.ChoiceField(
        choices=[
            ('None', 'None'),
            ('Pending', 'Pending'),
            ('Baseline', 'Baseline'),
            ('Negative Vetting 1', 'Negative Vetting 1'),
            ('Negative Vetting 2', 'Negative Vetting 2'),
            ('Positive Vetting', 'Positive Vetting')
        ],
        required=True
    )
    suburb = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # The profile is created by the signal so updatngi its fields:
            profile = user.profile
            profile.first_name = self.cleaned_data.get("first_name")
            profile.middle_name = self.cleaned_data.get("middle_name")
            profile.last_name = self.cleaned_data.get("last_name")
            profile.date_of_birth = self.cleaned_data.get("date_of_birth")
            profile.agvsa_clearance_number = self.cleaned_data.get("agvsa_clearance_number")
            profile.security_clearance = self.cleaned_data.get("security_clearance")
            profile.suburb = self.cleaned_data.get("suburb")
            profile.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", "is_active", "is_staff")

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

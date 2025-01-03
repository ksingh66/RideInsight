from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserRegistrationForm(UserCreationForm):
    """
    Form for registering new users. Extends UserCreationForm to handle
    custom fields and email-based authentication.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'company_name', 'password1', 'password2')
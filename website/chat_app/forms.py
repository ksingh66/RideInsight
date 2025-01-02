from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
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



class ApprovedUserAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # First check Django's default conditions (like is_active)
        super().confirm_login_allowed(user)
        
        # Then check our custom approval status
        if not user.is_approved:  # Assuming is_approved is a field in your CustomUser model
            raise ValidationError(
                "Your account is awaiting approval. Please contact the administrator.",
                code='account_not_approved'
            )
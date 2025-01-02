from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import os

# First, let's create a custom manager for our user model
class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        # Normalize the email address (converts domain part to lowercase)
        email = self.normalize_email(email)
        
        # Create the user instance
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        # Set default superuser properties
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('company_name', 'Admin Company')
        
        # Verify the user has necessary permissions
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        # Create the superuser using the create_user method
        return self.create_user(email, password, **extra_fields)

# Now let's update our CustomUser model to use this manager
class CustomUser(AbstractUser):
    """
    Custom user model that uses email for authentication instead of username.
    Extends Django's AbstractUser to maintain all default user functionality
    while modifying the authentication method.
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Must be a valid email address.')
    )
    is_approved = models.BooleanField(
        default=False,
        help_text='Whether the user is approved to use the website'
    )
    company_name = models.CharField(
        max_length=100,
        help_text=_('Name of the user company')
    )

    # Remove the username field
    username = None

    # Specify email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is automatically required

    # Assign the custom manager to our model
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UploadedCSV(models.Model):
    """
    Model to store and manage CSV files uploaded by users.
    Handles both the original CSV and its processed version.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use this instead of directly referencing AbstractUser
        on_delete=models.CASCADE,
        help_text=_('The user who uploaded this CSV file.')
    )
    raw_csv = models.FileField(
        upload_to='csv_files/',
        help_text=_('The original CSV file uploaded by the user.')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp of when the file was uploaded.')
    )
    processed_csv = models.FileField(
        upload_to='summaries/',
        null=True,
        help_text=_('The processed version of the CSV file.')
    )
    is_processed = models.BooleanField(
        default=False,
        help_text=_('Indicates whether the CSV has been processed.')
    )

    def __str__(self):
        """
        Returns a string representation using the user's email instead of username
        since we're using email-based authentication.
        """
        return f"{self.user.email}'s CSV - {self.uploaded_at}"

    def delete(self, *args, **kwargs):
        """
        Override delete method to ensure both the raw and processed files
        are removed from storage when the model instance is deleted.
        """
        # Delete the raw CSV file if it exists
        if self.raw_csv:
            file_path = self.raw_csv.path
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    # Log the error but don't prevent deletion of the model instance
                    print(f"Error deleting raw CSV file: {e}")

        # Delete the processed CSV file if it exists
        if self.processed_csv:
            file_path = self.processed_csv.path
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error deleting processed CSV file: {e}")

        # Call the parent class's delete method
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Uploaded CSV')
        verbose_name_plural = _('Uploaded CSVs')
        ordering = ['-uploaded_at']  # Newest files first
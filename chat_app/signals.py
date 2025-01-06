from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import CustomUser

@receiver(pre_save, sender=CustomUser)
def send_approval_email(sender, instance, **kwargs):
    """
    Signal handler to send an email when a user's approval status changes.
    Compares the current instance with the database instance to detect changes.
    """
    try:
        # Get the current database instance
        current_user = CustomUser.objects.get(pk=instance.pk)
        
        # Check if is_approved status has changed
        if current_user.is_approved != instance.is_approved:
            # Prepare email content
            context = {
                'user_email': instance.email,
                'company_name': instance.company_name,
                'status': 'approved' if instance.is_approved else 'unapproved'
            }
            
            # Render email templates
            html_message = render_to_string('emails/approval_status.html', context)
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject='Your Account Status Has Been Updated',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )
            
    except CustomUser.DoesNotExist:
        # This is a new user being created, no need to send approval email
        pass
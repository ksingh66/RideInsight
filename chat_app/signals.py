from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def notify_admin_new_user(sender, instance, created, **kwargs):
    """
    Signal handler to notify admin when a new user is created.
    """
    if created:
        # Prepare email content for admin notification
        admin_context = {
            'user_email': instance.email,
            'company_name': instance.company_name,
            'full_name': f"{instance.first_name} {instance.last_name}",
            'date_joined': instance.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Render admin notification email
        html_message = render_to_string('emails/new_user_admin_notification.html', admin_context)
        plain_message = strip_tags(html_message)
        
        # Send email to admin
        send_mail(
            subject=f'New User Registration: {instance.email}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],  # Make sure to define ADMIN_EMAIL in settings
            html_message=html_message,
            fail_silently=False,
        )

@receiver(pre_save, sender=CustomUser)
def send_approval_email(sender, instance, **kwargs):
    """
    Signal handler to send an email when a user's approval status changes.
    """
    try:
        current_user = CustomUser.objects.get(pk=instance.pk)
        if current_user.is_approved != instance.is_approved:
            context = {
                'user_email': instance.email,
                'company_name': instance.company_name,
                'status': 'approved' if instance.is_approved else 'unapproved'
            }
            
            html_message = render_to_string('emails/approval_status.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Your Account Status Has Been Updated',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )
            
    except CustomUser.DoesNotExist:
        pass  # This is a new user being created

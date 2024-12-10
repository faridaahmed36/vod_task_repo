from celery import shared_task
from datetime import timedelta, date
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Task, User

@shared_task
def send_subscription_reports():
    users = User.objects.filter(is_subscribed=True)
    for user in users:
        frequency = user.subscription_frequency
        if frequency == 'daily':
            date_range = date.today() - timedelta(days=1)
        elif frequency == 'weekly':
            date_range = date.today() - timedelta(days=7)
        elif frequency == 'monthly':
            date_range = date.today() - timedelta(days=30)
        else:
            continue

        # Filter tasks based on the end date
        tasks = Task.objects.filter(user=user, due_date__gte=date_range, due_date__lte=date.today())

        # Prepare and send the email
        html_content = render_to_string('email_template.html', {
            'user': user,
            'tasks': tasks,
            'frequency': frequency,
        })

        email = EmailMessage(
            subject=f"Your {frequency.capitalize()} Task Report",
            body=html_content,
            from_email='yourapp@example.com',
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send()

from django.db import models
from django.utils.timezone import now

class Members(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=100)
    

class Tasks(models.Model):
    title = models.CharField(max_length=200)
    description= models.CharField(max_length=500)
    start_date = models.DateField()
    due_date = models.DateField()
    completion_date = models.DateField(default="2024-12-9")
    status = models.CharField(max_length=50, default='Pending')
    owner = models.ForeignKey(Members, on_delete=models.CASCADE, related_name='tasks')
    deleted = models.BooleanField(default=False)  
    deleted_at = models.DateTimeField(null=True, blank=True)


class StatusChoices(models.TextChoices):
    PENDING = "Pending", "Pending"
    COMPLETED = "Completed", "Completed"
    OVERDUE = "Overdue", "Overdue"
        
status = models.CharField(
    max_length=10,
    choices=StatusChoices.choices,
    default=StatusChoices.PENDING,
)

class Subscription(models.Model):
    user = models.OneToOneField(Members, on_delete=models.CASCADE, related_name="subscription")
    start_date = models.DateField()
    frequency = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    report_time = models.TimeField()  # Only accepts hour values (no minutes)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
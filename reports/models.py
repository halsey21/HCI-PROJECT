from django.db import models
from django.contrib.auth.models import User
import uuid

class Report(models.Model):
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('VERIFIED', 'Verified'),
    ]

    ISSUE_TYPE_CHOICES = [
        ('MISSED_COLLECTION', 'Missed Collection'),
        ('ILLEGAL_DUMPING', 'Illegal Dumping'),
        ('OVERFLOWING_BIN', 'Overflowing Bin'),
        ('LITTERING', 'Littering'),
        ('POTHOLE', 'Pothole'),
        ('WATER_LEAK', 'Water Leak'),
        ('ELECTRICITY_OUTAGE', 'Electricity Outage'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('VERIFIED', 'Verified'),
    ]

    CONTACT_PREFERENCES = [
        ('SMS', 'SMS'),
        ('APP', 'App Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, default='MISSED_COLLECTION')
    photo = models.ImageField(upload_to='reports/photos/', blank=True, null=True)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    contact_preference = models.CharField(max_length=3, choices=CONTACT_PREFERENCES, default='APP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    assigned_crew = models.CharField(max_length=50, blank=True, null=True)
    tracking_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import random
            import string
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.reference_number = f'JOBURG-{suffix}'
            
            if not self.latitude or not self.longitude:
                # Johannesburg is roughly -26.2, 28.0
                self.latitude = -26.2 + (random.uniform(-0.1, 0.1))
                self.longitude = 28.0 + (random.uniform(-0.1, 0.1))
                
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference_number

class Support(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='supports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('report', 'user')

class Verification(models.Model):
    VERIFY_CHOICES = [
        ('CONFIRM', 'Confirmed'),
        ('DISPUTE', 'Disputed'),
    ]
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='verification')
    status = models.CharField(max_length=10, choices=VERIFY_CHOICES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_sms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-bell')
    color = models.CharField(max_length=50, default='text-blue')

    def __str__(self):
        return self.title

class CommunityFeed(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='feed_items')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feed for {self.report.reference_number}"

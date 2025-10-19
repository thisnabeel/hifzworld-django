from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import random
import string
from django.conf import settings

def generate_unique_code():
    return ''.join(random.choices(string.digits, k=6))

class MatchmakingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        pass
    
    def __str__(self):
        return f"Request from {self.requester} to {self.target_user} - {self.status}"

class Event(models.Model):
    PRIVACY_CHOICES = [
        (True, 'Private'),
        (False, 'Public'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_events')
    
    title = models.CharField(max_length=255)
    datetime = models.DateTimeField(default=now)
    time_zone = models.CharField(max_length=50, blank=True)  # Time zone as string (e.g., "America/New_York")
    duration = models.DurationField()  # Store duration as timedelta
    unique_code = models.CharField(max_length=6, unique=True, default=generate_unique_code, editable=False)
    is_private = models.BooleanField(choices=PRIVACY_CHOICES, default=True)
    peer_id = models.CharField(max_length=255, null=True, blank=True)  # ✅ Add this field

    def __str__(self):
        return f"{self.title} - {self.unique_code}"


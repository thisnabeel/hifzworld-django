from django.db import models
from django.utils.timezone import now
import random
import string
from django.conf import settings

def generate_unique_code():
    return ''.join(random.choices(string.digits, k=6))

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


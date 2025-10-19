from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import random
import string
from django.conf import settings

def generate_unique_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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


class Room(models.Model):
    """
    Persistent 1:1 rooms for PVP matches
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting for participants'),
        ('active', 'Active match'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Room identification
    room_code = models.CharField(max_length=8, unique=True, default=generate_room_code, editable=False)
    
    # Participants
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rooms_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rooms_as_user2')
    
    # Room metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='waiting')
    title = models.CharField(max_length=255, default='PVP Match')
    
    # Activity tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=now)
    
    # Session data
    session_id = models.CharField(max_length=255, null=True, blank=True)  # Links to Event if needed
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Room {self.room_code} - {self.user1.first_name} vs {self.user2.first_name if self.user2 else 'Waiting'}"
    
    def get_other_user(self, user):
        """Get the other participant in the room"""
        if self.user1 == user:
            return self.user2
        return self.user1
    
    def can_join(self, user):
        """Check if a user can join this room"""
        if self.status != 'waiting':
            return False
        
        # If room has space for a second user OR user is already in the room
        if not self.user2 or self.user1 == user or (self.user2 and self.user2 == user):
            return True
            
        return False
    
    def is_user_in_room(self, user):
        """Check if user is already in this room"""
        return self.user1 == user or (self.user2 and self.user2 == user)
    
    def mark_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = now()
        self.save(update_fields=['last_activity'])


class RoomParticipant(models.Model):
    """
    Track who is currently in the room (real-time)
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='room_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_connected = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=now)
    
    class Meta:
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.first_name} in Room {self.room.room_code}"


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


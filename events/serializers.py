from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, MatchmakingRequest
from django.utils.timezone import make_aware
from pytz import timezone  # ✅ Import for time zone conversion

# Get the User model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning all user details."""
    
    class Meta:
        model = User
        fields = '__all__'  # ✅ Include all user fields (modify if needed)

class EventSerializer(serializers.ModelSerializer):
    datetime_local = serializers.SerializerMethodField()  # ✅ Convert UTC to local time zone
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # ✅ Accepts only user ID

    class Meta:
        model = Event
        fields = ['id', 'title', 'datetime', 'datetime_local', 'time_zone', 'duration', 'is_private', 'user', 'peer_id']

    def get_datetime_local(self, obj):
        """Convert stored UTC datetime to the time zone saved in the database."""
        if obj.time_zone:
            try:
                # ✅ Convert UTC datetime to the stored time zone
                tz = timezone(obj.time_zone)  
                return obj.datetime.astimezone(tz).isoformat()
            except Exception as e:
                return str(e)  # ✅ Return error message if conversion fails
        return obj.datetime.isoformat()  # ✅ Default: return UTC datetime


class MatchmakingRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.SerializerMethodField()
    target_user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchmakingRequest
        fields = [
            'id', 'requester', 'target_user', 'status', 'created_at', 
            'updated_at', 'expires_at', 'session_id', 'requester_name', 'target_user_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_requester_name(self, obj):
        return f"{obj.requester.first_name} {obj.requester.last_name}".strip()
    
    def get_target_user_name(self, obj):
        return f"{obj.target_user.first_name} {obj.target_user.last_name}".strip()

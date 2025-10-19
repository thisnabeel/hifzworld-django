from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, MatchmakingRequest, Room, RoomParticipant
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


class RoomParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomParticipant
        fields = ['id', 'user', 'user_name', 'joined_at', 'is_connected', 'last_seen']
        read_only_fields = ['id', 'joined_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class RoomSerializer(serializers.ModelSerializer):
    user1_name = serializers.SerializerMethodField()
    user2_name = serializers.SerializerMethodField()
    other_user_name = serializers.SerializerMethodField()
    participants = RoomParticipantSerializer(many=True, read_only=True)
    can_join = serializers.SerializerMethodField()
    is_user_in_room = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_code', 'user1', 'user2', 'created_by', 'status', 'title',
            'created_at', 'updated_at', 'last_activity', 'session_id',
            'user1_name', 'user2_name', 'other_user_name', 'participants', 'can_join', 'is_user_in_room'
        ]
        read_only_fields = ['id', 'room_code', 'created_at', 'updated_at', 'last_activity']
    
    def get_user1_name(self, obj):
        return f"{obj.user1.first_name} {obj.user1.last_name}".strip()
    
    def get_user2_name(self, obj):
        if obj.user2:
            return f"{obj.user2.first_name} {obj.user2.last_name}".strip()
        return None
    
    def get_other_user_name(self, obj):
        """Get the name of the other user for the current context"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            other_user = obj.get_other_user(request.user)
            if other_user:
                return f"{other_user.first_name} {other_user.last_name}".strip()
        return None
    
    def get_can_join(self, obj):
        """Check if current user can join this room"""
        # First try to get user from context (for API calls)
        user_id = self.context.get('user_id')
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                return obj.can_join(user)
            except:
                pass
        
        # Fallback to request.user (for authenticated requests)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return obj.can_join(request.user)
        
        return False
    
    def get_is_user_in_room(self, obj):
        """Check if current user is already in this room"""
        # First try to get user from context (for API calls)
        user_id = self.context.get('user_id')
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                return obj.is_user_in_room(user)
            except:
                pass
        
        # Fallback to request.user (for authenticated requests)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            return obj.is_user_in_room(request.user)
        
        return False

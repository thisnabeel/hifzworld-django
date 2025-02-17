from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event
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
    user = UserSerializer()  # ✅ Nested serializer to include full user details

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

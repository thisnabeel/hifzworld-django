from rest_framework import serializers
from .models import UserProgressReport
from mushaf_page.serializers import MushafPageSerializer
from django.utils import timezone
from datetime import datetime

class UserProgressReportSerializer(serializers.ModelSerializer):
    mushaf_page = MushafPageSerializer()
    last_touched = serializers.SerializerMethodField()

    class Meta:
        model = UserProgressReport
        fields = [
            'user',
            'markings',
            'mushaf_page',
            'comment',
            'updated_at',
            'title',
            'last_touched'
        ]
        read_only_fields = ['updated_at']

    def get_last_touched(self, obj):
        if not obj.updated_at:
            return None

        now = timezone.now()
        diff = now - obj.updated_at

        # Convert timedelta to human-readable format
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"
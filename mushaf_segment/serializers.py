from rest_framework import serializers
from .models import MushafSegment

class MushafSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MushafSegment
        fields = '__all__'
from rest_framework import serializers
from .models import MissionSet, Mission

class MissionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionSet
        fields = ['id', 'title', 'position']

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['id', 'mission_set', 'question', 'verse_ref', 'surah_number', 'ayah_number', 'position']

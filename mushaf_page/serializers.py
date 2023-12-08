from rest_framework import serializers
from .models import MushafPage
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

class MushafPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MushafPage
        fields = '__all__'
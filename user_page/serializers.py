from rest_framework import serializers
from .models import UserPage
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

class UserPageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserPage
        fields = '__all__'

class CreateUserPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPage
        fields = ['id']

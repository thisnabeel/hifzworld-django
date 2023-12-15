from rest_framework import serializers
from .models import UserPage
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from mushaf_page.models import MushafPage

class UserPageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserPage
        fields = '__all__'

class CreateUserPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPage
        fields = ['id']


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPage
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Access the instance of the model and do something with it
        model_instance = instance  # This is the model instance being serialized

        # You can access its fields or perform any custom logic


        mushaf_page = model_instance.mushaf_page
        page_number = mushaf_page.page_number

        segment, percentage = mushaf_page.mushaf.get_segment_and_percentage(page_number)
        if segment:
            print(segment.title, percentage)
            representation['title'] = segment.title
            representation['percentage'] = percentage


        return representation
    

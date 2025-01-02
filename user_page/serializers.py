from rest_framework import serializers
from .models import UserPage
from mushaf_page.models import MushafPage
from datetime import datetime

class UserPageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()  # Add a custom method field

    class Meta:
        model = UserPage
        fields = '__all__'

    def get_created_at(self, obj):
        # Format created_at field to desired format
        if obj.created_at:
            return obj.created_at.strftime('%-m.%-d.%y %-I:%M%p')
        return None


class CreateUserPageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()  # Add a custom method field

    class Meta:
        model = UserPage
        fields = '__all__'

    def get_created_at(self, obj):
        # Format created_at field to desired format
        if obj.created_at:
            return obj.created_at.strftime('%-m.%-d.%y %-I:%M%p')
        return None

class UserProgressSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()  # Add the custom method field here too

    class Meta:
        model = UserPage
        fields = '__all__'

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%-m.%-d.%y %-I:%M%p')
        return None

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
            representation['page_number'] = page_number

        return representation

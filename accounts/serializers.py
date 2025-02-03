from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from branch.models import Branch  # Import the Branch model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'password', 'starting_verse_boundary', 'ending_verse_boundary', 'peer_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(**validated_data, password=password)

        Branch.objects.create(
            title="main",  # Default title
            position=1,           # First position
            user=user            # Associate with the new user
        )

        return user
    
class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = get_user_model().objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect email or password.")

        data['user'] = user
        return data
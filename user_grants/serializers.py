from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserGrant

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class UserGrantSerializer(serializers.ModelSerializer):
    granter_email = serializers.EmailField(write_only=True)
    grantee_email = serializers.EmailField(write_only=True)
    granter = UserSerializer(read_only=True)
    grantee = UserSerializer(read_only=True)

    class Meta:
        model = UserGrant
        fields = ['id', 'granter', 'grantee', 'granter_email', 'grantee_email', 'access_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        granter_email = validated_data.pop('granter_email')
        grantee_email = validated_data.pop('grantee_email')
        
        try:
            granter = User.objects.get(email=granter_email)
            grantee = User.objects.get(email=grantee_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        return UserGrant.objects.create(
            granter=granter,
            grantee=grantee,
            **validated_data
        )
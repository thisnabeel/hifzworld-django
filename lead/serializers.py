from rest_framework import serializers
from .models import Lead

class CreateLeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = ['email']

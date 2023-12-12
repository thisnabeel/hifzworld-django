from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateLeadSerializer



# Create your views here.
from rest_framework import status
from rest_framework.response import Response

from .models import Lead

class CreateLeadView(APIView):
    def post(self, request):
        serializer = CreateLeadSerializer(data=request.data)
        if serializer.is_valid():
            lead = serializer.save()
            return Response({'id': lead.id, 'email': lead.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

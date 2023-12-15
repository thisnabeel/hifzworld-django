from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserPageSerializer, CreateUserPageSerializer, UserProgressSerializer
from .models import UserPage
from rest_framework.authtoken.views import ObtainAuthToken
from mushaf_page.models import MushafPage
from django.contrib.auth import get_user_model

class CreateUserPageView(APIView):
    def post(self, request):
        serializer = CreateUserPageSerializer(data=request.data)
        if serializer.is_valid():
            # Using get_or_create to find or create a UserPage
            user_id = request.data['user_id']
            mushaf_page_id = request.data['mushaf_page_id']
            print(mushaf_page_id)
            user_page, created = UserPage.objects.get_or_create(
                user=get_user_model().objects.get(id=user_id),
                mushaf_page=MushafPage.objects.get(id=mushaf_page_id),
                defaults=request.data  # Additional fields to set when creating a new object
            )

            if created:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response("UserPage already exists", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPageView(APIView):
    def get(self, request, user_id, mushaf_page_id):
        user_page = UserPage.objects.filter(mushaf_page_id=mushaf_page_id, user_id=user_id).first()
        serializer = UserPageSerializer(user_page)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserProgressView(APIView):
    def get(self, request, user_id):
        user_page = UserPage.objects.filter(user_id=user_id)
        serializer = UserProgressSerializer(user_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
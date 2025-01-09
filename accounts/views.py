from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, SignInSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken

class CreateUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignInView(APIView):
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            print(f"User {user.id} successfully authenticated.")
            return Response({'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'gender': user.gender}, status=status.HTTP_200_OK)
        else:
            print("Authentication failed.")
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


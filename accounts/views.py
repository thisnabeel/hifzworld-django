from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, SignInSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

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

class UpdateUserView(APIView):
    # permission_classes = [IsAuthenticated]
    
    def put(self, request, user_id):
        # Get the user instance
        user = get_object_or_404(get_user_model(), id=user_id)
        
        # # Check if the authenticated user is trying to update their own data
        # if request.user.id != user.id:
        #     return Response(
        #         {"error": "You don't have permission to update this user's data"},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        # Update only the fields that are provided
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'gender': user.gender,
                'starting_verse_boundary': user.starting_verse_boundary,
                'ending_verse_boundary': user.ending_verse_boundary
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        # PATCH method for partial updates
        return self.put(request, user_id)
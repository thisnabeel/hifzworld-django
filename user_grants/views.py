# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserGrant
from .serializers import UserGrantSerializer

User = get_user_model()

class UserGrantView(APIView):
    def post(self, request):
        try:
            granter_email = request.data.get('granter_email')
            grantee_email = request.data.get('grantee_email')
            access_type = request.data.get('access_type')

            granter = User.objects.get(email=granter_email)
            grantee = User.objects.get(email=grantee_email)

            user_grant = UserGrant.objects.create(
                granter=granter,
                grantee=grantee,
                access_type=access_type
            )

            serializer = UserGrantSerializer(user_grant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {"error": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            granted_permissions = UserGrant.objects.filter(
                granter=user, 
                is_active=True
            )
            received_permissions = UserGrant.objects.filter(
                grantee=user, 
                is_active=True
            )

            return Response({
                'granted_permissions': UserGrantSerializer(granted_permissions, many=True).data,
                'received_permissions': UserGrantSerializer(received_permissions, many=True).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class RevokeGrantView(APIView):
    def post(self, request, grant_id):
        try:
            grant = UserGrant.objects.get(id=grant_id)
            grant.is_active = False
            grant.save()
            
            return Response({
                "message": f"Access revoked for {grant.grantee.email}"
            }, status=status.HTTP_200_OK)
            
        except UserGrant.DoesNotExist:
            return Response(
                {"error": "Grant not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
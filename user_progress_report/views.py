from django.shortcuts import render
from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserProgressReport
from .serializers import UserProgressReportSerializer
from django.contrib.auth import get_user_model

class UserProgressReportListView(APIView):
    def get(self, request, user_id):
        user = get_user_model().objects.get(id=user_id)
        reports = UserProgressReport.objects.filter(user=user)
        serializer = UserProgressReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

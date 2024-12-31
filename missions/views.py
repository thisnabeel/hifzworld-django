from django.shortcuts import render
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from rest_framework import generics
from .models import MissionSet, Mission
from .serializers import MissionSetSerializer, MissionSerializer

# MissionSet Views
class MissionSetListCreateView(generics.ListCreateAPIView):
    queryset = MissionSet.objects.all()
    serializer_class = MissionSetSerializer

class MissionSetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MissionSet.objects.all()
    serializer_class = MissionSetSerializer

# Mission Views
class MissionListCreateView(generics.ListCreateAPIView):
    serializer_class = MissionSerializer

    def get_queryset(self):
        mission_set_id = self.kwargs['mission_set_id']
        return Mission.objects.filter(mission_set_id=mission_set_id)

    def perform_create(self, serializer):
        mission_set_id = self.kwargs['mission_set_id']
        mission_set = MissionSet.objects.get(id=mission_set_id)
        serializer.save(mission_set=mission_set)

class MissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

class RandomMissionView(APIView):
    def get(self, request):
        mission_count = Mission.objects.count()
        if mission_count == 0:
            raise NotFound("No missions available.")
        random_index = random.randint(0, mission_count - 1)
        random_mission = Mission.objects.all()[random_index]
        serializer = MissionSerializer(random_mission)
        return Response(serializer.data)
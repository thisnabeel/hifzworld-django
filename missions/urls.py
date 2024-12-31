from django.urls import path
from .views import (
    MissionSetListCreateView, MissionSetDetailView,
    MissionListCreateView, MissionDetailView,
    RandomMissionView
)

urlpatterns = [
    # MissionSet endpoints
    path('mission_sets/', MissionSetListCreateView.as_view(), name='mission_set_list_create'),
    path('mission_sets/<int:pk>/', MissionSetDetailView.as_view(), name='mission_set_detail'),

    # Mission endpoints (nested under MissionSet)
    path('mission_sets/<int:mission_set_id>/missions/', MissionListCreateView.as_view(), name='mission_list_create'),
    path('missions/<int:pk>/', MissionDetailView.as_view(), name='mission_detail'),

    path('missions/random/', RandomMissionView.as_view(), name='random_mission_detail'),

]

from django.urls import path
from .views import (
    EventListCreateView, EventListView, EventDetailView, FriendsEventsView, 
    UpdateEventPeerIDView, OnlineFriendsView, UpdateOnlineStatusView,
    CreateMatchmakingRequestView, MatchmakingRequestActionView, UserMatchmakingRequestsView
)

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:event_id>/', EventDetailView.as_view(), name='event-list-create'),
    path('events/users/<int:user_id>', EventListView.as_view(), name='event-detail'),
    path('events/users/<int:user_id>/friends', FriendsEventsView.as_view(), name='friends-events'),
    path('events/<int:event_id>/update_peer_id/', UpdateEventPeerIDView.as_view(), name="update-event-peer-id"),
    
    # PVP Matchmaking endpoints
    path('users/<int:user_id>/online-friends/', OnlineFriendsView.as_view(), name='online-friends'),
    path('users/<int:user_id>/update-status/', UpdateOnlineStatusView.as_view(), name='update-online-status'),
    path('matchmaking/request/', CreateMatchmakingRequestView.as_view(), name='create-matchmaking-request'),
    path('matchmaking/request/<int:request_id>/action/', MatchmakingRequestActionView.as_view(), name='matchmaking-request-action'),
    path('users/<int:user_id>/matchmaking-requests/', UserMatchmakingRequestsView.as_view(), name='user-matchmaking-requests'),
]

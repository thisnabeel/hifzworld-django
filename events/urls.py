from django.urls import path
from .views import (
    EventListCreateView, EventListView, EventDetailView, FriendsEventsView, 
    UpdateEventPeerIDView, OnlineFriendsView, UpdateOnlineStatusView,
    CreateMatchmakingRequestView, MatchmakingRequestActionView, UserMatchmakingRequestsView,
    UpdateMatchStatusView, CreateRoomView, UserRoomsView, JoinRoomView, LeaveRoomView, EnterRoomView
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
    path('matchmaking/request/<int:request_id>/status/', UpdateMatchStatusView.as_view(), name='update-match-status'),
    path('users/<int:user_id>/matchmaking-requests/', UserMatchmakingRequestsView.as_view(), name='user-matchmaking-requests'),
    
    # Room endpoints
    path('rooms/create/', CreateRoomView.as_view(), name='create-room'),
    path('users/<int:user_id>/rooms/', UserRoomsView.as_view(), name='user-rooms'),
    path('rooms/<int:room_id>/join/', JoinRoomView.as_view(), name='join-room'),
    path('rooms/<int:room_id>/enter/', EnterRoomView.as_view(), name='enter-room'),
    path('rooms/<int:room_id>/leave/', LeaveRoomView.as_view(), name='leave-room'),
]

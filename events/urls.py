from django.urls import path
from .views import EventListCreateView, EventListView, EventDetailView, FriendsEventsView, UpdateEventPeerIDView

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/users/<int:user_id>', EventListView.as_view(), name='event-detail'),
    path('events/users/<int:user_id>/friends', FriendsEventsView.as_view(), name='friends-events'),  # ✅ New Route
    path('events/<int:event_id>/update_peer_id/', UpdateEventPeerIDView.as_view(), name="update-event-peer-id")
]

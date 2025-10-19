from django.urls import re_path
from events.consumers import WebRTCConsumer, MatchmakingConsumer

websocket_urlpatterns = [
    re_path(r'ws/signaling/(?P<event_code>\w+)/$', WebRTCConsumer.as_asgi()),
    re_path(r'ws/matchmaking/(?P<user_id>\d+)/$', MatchmakingConsumer.as_asgi()),
]

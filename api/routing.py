from django.urls import re_path
from events.consumers import WebRTCConsumer

websocket_urlpatterns = [
    re_path(r'ws/signaling/(?P<event_code>\w+)/$', WebRTCConsumer.as_asgi()),
]

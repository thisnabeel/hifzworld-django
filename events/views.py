from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer
from rest_framework import generics
from user_grants.models import UserGrant  # ✅ Import UserGrant model
from django.utils.timezone import now
import pytz  # ✅ Import pytz for timezone handling


class EventListCreateView(APIView):
    """
    API to list all events or create a new event.
    """

    def get(self, request):
        user_timezone = request.GET.get("timezone", "UTC")  # Get timezone from request, default to UTC

        try:
            timezone = pytz.timezone(user_timezone)  # Convert to pytz timezone
        except pytz.UnknownTimeZoneError:
            return Response({"error": "Invalid timezone"}, status=status.HTTP_400_BAD_REQUEST)

        current_time = now().astimezone(timezone)  # Convert current time to user's timezone
        events = Event.objects.filter(datetime__gt=current_time)  # Filter future events
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        print("Received Data:", request.data)  # ✅ Debugging
        serializer = EventSerializer(data=request.data)
        
        if serializer.is_valid():
            event = serializer.save()

            # ✅ If no peer_id was provided, the first user should generate it later
            if "peer_id" not in request.data or not request.data["peer_id"]:
                event.peer_id = None
                event.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errors:", serializer.errors)  # ✅ Debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateEventPeerIDView(APIView):
    """
    API endpoint to update the peer ID of an event.
    """

    def patch(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        # ✅ Ensure peer_id is only set once
        if event.peer_id:
            return Response({"error": "Peer ID is already set and cannot be changed."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Update peer_id
        peer_id = request.data.get("peer_id")
        if not peer_id:
            return Response({"error": "Peer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        event.peer_id = peer_id
        event.save()
        return Response({"message": "Peer ID updated successfully.", "peer_id": event.peer_id}, status=status.HTTP_200_OK)
    
class EventListView(APIView):
    """
    API to get all events for a specific user.
    """

    def get(self, request, user_id):
        events = Event.objects.filter(user_id=user_id)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EventDetailView(APIView):
    """
    API endpoint for retrieving, updating, and deleting a single event.
    """

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class FriendsEventsView(APIView):
    """
    API endpoint to get events from users who have granted access to the requesting user.
    """

    def get(self, request, user_id):
        # ✅ Get all users who have granted access to the requesting user
        granted_users = UserGrant.objects.filter(grantee_id=user_id, is_active=True).values_list('granter_id', flat=True)

        # ✅ Fetch events from those users
        events = Event.objects.filter(user_id__in=granted_users)

        # ✅ Serialize and return the events
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

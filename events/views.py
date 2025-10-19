from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, MatchmakingRequest
from .serializers import EventSerializer, MatchmakingRequestSerializer
from rest_framework import generics
from user_grants.models import UserGrant  # ✅ Import UserGrant model
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Q
import pytz
import uuid

User = get_user_model()


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


class OnlineFriendsView(APIView):
    """
    API endpoint to get online friends for PVP matching
    """
    
    def get(self, request, user_id):
        # Get all friends (users who have granted access or have received grants)
        friend_grants = UserGrant.objects.filter(
            Q(grantee_id=user_id) | Q(granter_id=user_id),
            is_active=True
        )
        
        # Get friend IDs (excluding the current user)
        friend_ids = set()
        for grant in friend_grants:
            if grant.grantee_id == user_id:
                friend_ids.add(grant.granter_id)
            else:
                friend_ids.add(grant.grantee_id)
        
        # Get online friends who are available for matching
        online_friends = User.objects.filter(
            id__in=friend_ids,
            is_online=True,
            is_available_for_match=True
        ).exclude(id=user_id)
        
        # Serialize friend data
        friends_data = []
        for friend in online_friends:
            friends_data.append({
                'id': friend.id,
                'first_name': friend.first_name,
                'last_name': friend.last_name,
                'email': friend.email,
                'last_seen': friend.last_seen.isoformat(),
                'is_online': friend.is_online,
                'is_available_for_match': friend.is_available_for_match
            })
        
        return Response(friends_data, status=status.HTTP_200_OK)


class UpdateOnlineStatusView(APIView):
    """
    API endpoint to update user's online status
    """
    
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        is_online = request.data.get('is_online', False)
        is_available_for_match = request.data.get('is_available_for_match', True)
        
        user.is_online = is_online
        user.is_available_for_match = is_available_for_match
        user.last_seen = now()
        user.save()
        
        return Response({
            'message': 'Status updated successfully',
            'is_online': user.is_online,
            'is_available_for_match': user.is_available_for_match,
            'last_seen': user.last_seen.isoformat()
        }, status=status.HTTP_200_OK)


class CreateMatchmakingRequestView(APIView):
    """
    API endpoint to create a matchmaking request
    """
    
    def post(self, request):
        requester_id = request.data.get('requester_id')
        target_user_id = request.data.get('target_user_id')
        
        if not requester_id or not target_user_id:
            return Response(
                {'error': 'Both requester_id and target_user_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if requester_id == target_user_id:
            return Response(
                {'error': 'Cannot send request to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        requester = get_object_or_404(User, id=requester_id)
        target_user = get_object_or_404(User, id=target_user_id)
        
        # Check if target user is online and available
        if not target_user.is_online or not target_user.is_available_for_match:
            return Response(
                {'error': 'Target user is not available for matching'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already a pending request
        existing_request = MatchmakingRequest.objects.filter(
            requester=requester,
            target_user=target_user,
            status='pending'
        ).first()
        
        if existing_request:
            return Response(
                {'error': 'A pending request already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from datetime import timedelta
        # Create new request
        request_obj = MatchmakingRequest.objects.create(
            requester=requester,
            target_user=target_user,
            expires_at=now() + timedelta(minutes=2),
            session_id=str(uuid.uuid4())
        )
        
        serializer = MatchmakingRequestSerializer(request_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MatchmakingRequestActionView(APIView):
    """
    API endpoint to accept/decline matchmaking requests
    """
    
    def post(self, request, request_id):
        match_request = get_object_or_404(MatchmakingRequest, id=request_id)
        action = request.data.get('action')  # 'accept' or 'decline'
        
        if action not in ['accept', 'decline']:
            return Response(
                {'error': 'Action must be either "accept" or "decline"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if match_request.status != 'pending':
            return Response(
                {'error': 'Request is no longer pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'accept':
            match_request.status = 'accepted'
            # Create a temporary event for the match
            from datetime import timedelta
            event = Event.objects.create(
                user=match_request.requester,
                invited_user=match_request.target_user,
                title=f"PVP Match - {match_request.requester.first_name} vs {match_request.target_user.first_name}",
                datetime=now(),
                duration=timedelta(minutes=30),
                is_private=True,
                unique_code=match_request.session_id[:6]
            )
            match_request.session_id = str(event.id)
        else:
            match_request.status = 'declined'
        
        match_request.save()
        
        serializer = MatchmakingRequestSerializer(match_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMatchmakingRequestsView(APIView):
    """
    API endpoint to get user's matchmaking requests (sent and received)
    """
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        sent_requests = MatchmakingRequest.objects.filter(requester=user)
        received_requests = MatchmakingRequest.objects.filter(target_user=user)
        
        sent_serializer = MatchmakingRequestSerializer(sent_requests, many=True)
        received_serializer = MatchmakingRequestSerializer(received_requests, many=True)
        
        return Response({
            'sent_requests': sent_serializer.data,
            'received_requests': received_serializer.data
        }, status=status.HTTP_200_OK)

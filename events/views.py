from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, MatchmakingRequest, Room, RoomParticipant
from .serializers import EventSerializer, MatchmakingRequestSerializer, RoomSerializer, RoomParticipantSerializer
from rest_framework import generics
from user_grants.models import UserGrant  # ✅ Import UserGrant model
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pytz
import uuid
from datetime import timedelta

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


class UpdateMatchStatusView(APIView):
    """
    API endpoint to update matchmaking request status when user enters room
    """
    
    def post(self, request, request_id):
        match_request = get_object_or_404(MatchmakingRequest, id=request_id)
        action = request.data.get('action')  # 'enter_room' or 'leave_room'
        user_id = request.data.get('user_id')  # We'll pass this from frontend
        
        if action == 'enter_room':
            match_request.status = 'in_progress'
            match_request.save()
            
            # Determine the other participant
            if user_id == match_request.requester.id:
                other_user_id = match_request.target_user.id
                entering_user_name = f"{match_request.requester.first_name} {match_request.requester.last_name}".strip()
            else:
                other_user_id = match_request.requester.id
                entering_user_name = f"{match_request.target_user.first_name} {match_request.target_user.last_name}".strip()
            
            # Send WebSocket notification to the other participant
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"matchmaking_{other_user_id}",
                    {
                        'type': 'match_status_update',
                        'message': {
                            'type': 'user_entered_room',
                            'match_request_id': match_request.id,
                            'user_name': entering_user_name,
                            'status': 'in_progress'
                        }
                    }
                )
            
        elif action == 'leave_room':
            # Could revert to 'accepted' or handle differently
            pass
        
        serializer = MatchmakingRequestSerializer(match_request)
        return Response({
            'match_request': serializer.data,
            'message': 'Match status updated successfully'
        }, status=status.HTTP_200_OK)


class CreateRoomView(APIView):
    """
    API endpoint to create a new room for PVP match
    """
    
    def post(self, request):
        user_id = request.data.get('user_id')
        target_user_id = request.data.get('target_user_id')
        title = request.data.get('title', 'PVP Match')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            creator = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If target_user_id is provided, get that user
        target_user = None
        if target_user_id:
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create the room
        room = Room.objects.create(
            user1=creator,
            user2=target_user,
            created_by=creator,
            title=title,
            status='waiting' if target_user else 'waiting'
        )
        
        # If target user is specified, notify them via WebSocket
        if target_user:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"matchmaking_{target_user.id}",
                    {
                        'type': 'room_notification',
                        'message': {
                            'type': 'room_created',
                            'room_id': room.id,
                            'room_code': room.room_code,
                            'creator_name': f"{creator.first_name} {creator.last_name}".strip(),
                            'title': title
                        }
                    }
                )
        
        serializer = RoomSerializer(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRoomsView(APIView):
    """
    API endpoint to get rooms for a user (created by them or they can join)
    """
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get rooms where user is participant or can join
        rooms = Room.objects.filter(
            Q(user1=user) | Q(user2=user) | Q(user2__isnull=True)
        ).filter(
            Q(status='waiting') | Q(status='active')
        )
        
        serializer = RoomSerializer(rooms, many=True, context={'request': request, 'user_id': user_id})
        return Response({
            'rooms': serializer.data
        }, status=status.HTTP_200_OK)


class JoinRoomView(APIView):
    """
    API endpoint to join a room
    """
    
    def post(self, request, room_id):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            room = Room.objects.get(id=room_id)
        except (User.DoesNotExist, Room.DoesNotExist):
            return Response({'error': 'User or room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not room.can_join(user):
            return Response({'error': 'Cannot join this room'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is already in the room
        user_already_in_room = room.is_user_in_room(user)
        
        # If this is the room creator entering, create session if not exists
        if room.user1 == user and not room.session_id:
            # Room creator is entering for the first time, create event/session
            event = Event.objects.create(
                user=room.user1,
                invited_user=room.user2,  # Will be None if no one has joined yet
                title=room.title,
                duration=timedelta(hours=1),  # Default 1 hour duration
                is_private=True
            )
            room.session_id = str(event.id)
            room.save()
        
        # If user is not yet assigned as user2, assign them
        elif not room.user2 and room.user1 != user:
            room.user2 = user
            room.status = 'active'
            
            # Update the existing event to include the second user
            if room.session_id:
                try:
                    event = Event.objects.get(id=room.session_id)
                    event.invited_user = room.user2
                    event.save()
                except Event.DoesNotExist:
                    pass
            
            # Notify the creator
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"matchmaking_{room.user1.id}",
                    {
                        'type': 'room_notification',
                        'message': {
                            'type': 'user_joined_room',
                            'room_id': room.id,
                            'room_code': room.room_code,
                            'joiner_name': f"{user.first_name} {user.last_name}".strip()
                        }
                    }
                )
        
        # Create or update RoomParticipant
        participant, created = RoomParticipant.objects.get_or_create(
            room=room,
            user=user,
            defaults={'is_connected': True}
        )
        if not created:
            participant.is_connected = True
            participant.save()
        
        # Update room last activity
        room.mark_activity()
        
        serializer = RoomSerializer(room, context={'request': request, 'user_id': user_id})
        return Response({
            'room': serializer.data,
            'joined': created,
            'user_already_in_room': user_already_in_room
        }, status=status.HTTP_200_OK)


class EnterRoomView(APIView):
    """
    API endpoint to enter a room directly by ID (for /room/:id URLs)
    """
    
    def get(self, request, room_id):
        """Get room details for entering"""
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomSerializer(room, context={'request': request})
        return Response({
            'room': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, room_id):
        """Enter room - same as join but with different semantics"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            room = Room.objects.get(id=room_id)
        except (User.DoesNotExist, Room.DoesNotExist):
            return Response({'error': 'User or room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user can join this room (already checked in can_join method)
        if not room.can_join(user):
            return Response({'error': 'Cannot enter this room'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If this is the room creator entering, create session if not exists
        if room.user1 == user and not room.session_id:
            # Room creator is entering for the first time, create event/session
            event = Event.objects.create(
                user=room.user1,
                invited_user=room.user2,  # Will be None if no one has joined yet
                title=room.title,
                duration=timedelta(hours=1),  # Default 1 hour duration
                is_private=True
            )
            room.session_id = str(event.id)
            room.save()
        
        # If user is not yet assigned as user2, assign them
        elif not room.user2 and room.user1 != user:
            room.user2 = user
            room.status = 'active'
            
            # Update the existing event to include the second user
            if room.session_id:
                try:
                    event = Event.objects.get(id=room.session_id)
                    event.invited_user = room.user2
                    event.save()
                except Event.DoesNotExist:
                    pass
            
            # Notify the creator
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"matchmaking_{room.user1.id}",
                    {
                        'type': 'room_notification',
                        'message': {
                            'type': 'user_joined_room',
                            'room_id': room.id,
                            'room_code': room.room_code,
                            'joiner_name': f"{user.first_name} {user.last_name}".strip()
                        }
                    }
                )
        
        # Create or update RoomParticipant
        participant, created = RoomParticipant.objects.get_or_create(
            room=room,
            user=user,
            defaults={'is_connected': True}
        )
        if not created:
            participant.is_connected = True
            participant.save()
        
        # Update room last activity
        room.mark_activity()
        
        serializer = RoomSerializer(room, context={'request': request, 'user_id': user_id})
        return Response({
            'room': serializer.data,
            'entered': True
        }, status=status.HTTP_200_OK)


class LeaveRoomView(APIView):
    """
    API endpoint to leave a room
    """
    
    def post(self, request, room_id):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            room = Room.objects.get(id=room_id)
        except (User.DoesNotExist, Room.DoesNotExist):
            return Response({'error': 'User or room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update or remove RoomParticipant
        try:
            participant = RoomParticipant.objects.get(room=room, user=user)
            participant.is_connected = False
            participant.save()
        except RoomParticipant.DoesNotExist:
            pass
        
        # Update room last activity
        room.mark_activity()
        
        # Notify the other user
        other_user = room.get_other_user(user)
        if other_user:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"matchmaking_{other_user.id}",
                    {
                        'type': 'room_notification',
                        'message': {
                            'type': 'user_left_room',
                            'room_id': room.id,
                            'room_code': room.room_code,
                            'leaver_name': f"{user.first_name} {user.last_name}".strip()
                        }
                    }
                )
        
        return Response({
            'message': 'Successfully left room'
        }, status=status.HTTP_200_OK)

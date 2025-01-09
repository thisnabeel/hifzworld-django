from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from user_page.serializers import UserPageSerializer
from rest_framework.response import Response
from rest_framework import status
from collections import defaultdict
from django.utils.timezone import now
from datetime import timedelta

class StatsView(APIView):
    def get(self, request, user_id):
        # Validate user_id
        if not user_id:
            return JsonResponse({'error': 'user_id parameter is required'}, status=400)

        # Fetch the user or return 404 if not found
        user = get_object_or_404(get_user_model(), id=user_id)

        # Fetch user_pages (commits) related to the user
        user_pages = user.user_pages.all()

        # Define the threshold for "rusty" status (e.g., 30 days)
        rusty_threshold = timedelta(days=7)

        # Group the data by mushaf_page and calculate the "rusty" status
        grouped_data = defaultdict(lambda: {'page_number': None, 'pages': [], 'rusty': True, 'last_commit': None})
        for user_page in user_pages:
            mushaf_page_id = user_page.mushaf_page.id
            page_number = user_page.mushaf_page.page_number
            created_at = user_page.created_at

            # Update the group data
            grouped_data[mushaf_page_id]['page_number'] = page_number
            grouped_data[mushaf_page_id]['pages'].append({
                'id': user_page.id,
                'created_at': created_at,
                'branch': user_page.branch.id,
                'camped': user_page.camped,
                'drawn_paths': user_page.drawn_paths,
            })

            # Update the last commit date for the mushaf_page
            if not grouped_data[mushaf_page_id]['last_commit'] or created_at > grouped_data[mushaf_page_id]['last_commit']:
                grouped_data[mushaf_page_id]['last_commit'] = created_at

        # Determine "rusty" status for each mushaf_page
        for mushaf_page_id, data in grouped_data.items():
            last_commit = data['last_commit']
            if last_commit and (now() - last_commit) <= rusty_threshold:
                data['rusty'] = False

        # Prepare the response
        response_data = {
            'user': {
                'id': user.id,
                'email': user.email,
            },
            'grouped_user_pages': [
                {
                    'mushaf_page_id': mushaf_page_id,
                    'page_number': data['page_number'],
                    'pages': data['pages'],
                    'rusty': data['rusty'],
                    'last_commit': data['last_commit'],
                }
                for mushaf_page_id, data in grouped_data.items()
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserPageSerializer, CreateUserPageSerializer, UserProgressSerializer
from .models import UserPage
from rest_framework.authtoken.views import ObtainAuthToken
from mushaf_page.models import MushafPage
from branch.models import Branch
from django.contrib.auth import get_user_model
from itertools import groupby
from operator import itemgetter
from django.shortcuts import render
from operator import attrgetter
import random
from random import choice
from django.db.models import Max


class CreateUserPageView(APIView):
    def post(self, request):
        serializer = CreateUserPageSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.data['user']
            mushaf_page_id = request.data['mushaf_page']
            branch_id = request.data['branch']

            try:
                # Create a new UserPage instance
                user_page = UserPage.objects.create(
                    user=get_user_model().objects.get(id=user_id),
                    mushaf_page=MushafPage.objects.get(id=mushaf_page_id),
                    branch=Branch.objects.get(id=branch_id),
                    drawn_paths=request.data.get('drawn_paths', []),
                    camped=request.data.get('camped', False)
                )
                serializer = CreateUserPageSerializer(user_page)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserPageView(APIView):
    def get(self, request, user_id, mushaf_page_id, branch_id):
        user_pages = UserPage.objects.filter(
            mushaf_page_id=mushaf_page_id, 
            user_id=user_id, 
            branch_id=branch_id
        ).order_by('-created_at')
        
        serializer = UserPageSerializer(user_pages, many=True)  # Set many=True to serialize multiple objects
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserProgressView(APIView):
    def get(self, request, user_id):
        queryset = UserPage.objects.filter(user_id=user_id).order_by('mushaf_page')

        for page in queryset:
            segment, percentage = page.mushaf_page.mushaf.get_segment_and_percentage(page.mushaf_page.page_number)  # Add your custom value here
            if segment is not None:
                page.segment = segment.id
            else:
                page.segment = -1


        key_function = attrgetter('segment')

        # Sort the queryset based on the 'segment' attribute
        queryset = sorted(queryset, key=key_function)

        # Use groupby to group the queryset by the 'segment' attribute
        grouped_data = {}
        for key, group in groupby(queryset, key=key_function):
            grouped_data[key] = list(group)


        filtered_dict = {key: [pages[-1]] for key, pages in grouped_data.items() if key > -1}
        for key in filtered_dict.keys():
            value = filtered_dict[key]
            print(key, value)

        queryset = [page for pages in filtered_dict.values() for page in pages]

        serializer = UserProgressSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class RandomUserPageView(APIView):
    def get(self, request, user_id):
        # Step 1: Get the latest UserPage for each mushaf_page where drawn_paths is not null and not empty
        newest_user_pages = (
            UserPage.objects.filter(user_id=user_id, drawn_paths__isnull=False)
            .exclude(drawn_paths=[])
            .values('mushaf_page')  # Group by mushaf_page
            .annotate(latest_created_at=Max('created_at'))  # Get the latest created_at for each mushaf_page
        )

        # Step 2: Fetch the actual UserPage instances for the latest entries
        newest_user_page_ids = [
            UserPage.objects.filter(
                mushaf_page=data['mushaf_page'],
                created_at=data['latest_created_at']
            ).first().id
            for data in newest_user_pages
        ]

        # Step 3: Fetch the UserPages that are the latest for each mushaf_page
        user_pages = UserPage.objects.filter(id__in=newest_user_page_ids)

        # Step 4: Filter the pages with drawn_paths that contains an array with more than 10 objects
        filtered_user_pages = []
        for page in user_pages:
            # Check each array in drawn_paths and find if any array has more than 10 objects
            for drawn_path_array in page.drawn_paths:
                if isinstance(drawn_path_array, list) and len(drawn_path_array) > 10:
                    filtered_user_pages.append(page)
                    break  # No need to check further if one array matches the condition

        if not filtered_user_pages:
            return Response({"message": "No UserPages found with drawn_paths arrays having more than 10 objects"},
                            status=status.HTTP_404_NOT_FOUND)

        # Step 5: Select a random UserPage from the filtered pages
        random_user_page = choice(filtered_user_pages)

        # Step 6: Serialize and return the random UserPage
        serializer = UserPageSerializer(random_user_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
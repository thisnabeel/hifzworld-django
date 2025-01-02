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

        # for page in user_pages:
        #     if page 
        # mushaf_page.mushaf.get_segment_and_percentage(page_number)
        serializer = UserProgressSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
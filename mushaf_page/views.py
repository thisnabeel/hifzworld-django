from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MushafPage
from .serializers import MushafPageSerializer

class MushafPageView(APIView):
    def get(self, request, mushaf_id, page_number):
        # Retrieve the MushafPage object based on mushaf_id and page_number
        mushaf_page = get_object_or_404(MushafPage, mushaf_id=mushaf_id, page_number=page_number)

        serializer = MushafPageSerializer(mushaf_page)

        serialized_data = serializer.data
        serialized_data['image_s3_url'] = serializer.get_s3_url(mushaf_page)

        # Return the serialized data in the response
        return Response(serialized_data, status=status.HTTP_200_OK)
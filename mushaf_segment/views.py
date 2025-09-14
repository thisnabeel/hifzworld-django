from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MushafSegmentSerializer
from .models import MushafSegment
from rest_framework.authtoken.views import ObtainAuthToken
from mushaf.models import Mushaf


class MushafSegmentsView(APIView):
    def post(self, request):
        serializer = MushafSegmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, mushaf_id):
        # Perform the query and order by category_position
        mushaf_segments = MushafSegment.objects.filter(mushaf_id=mushaf_id).order_by('category_position')

        # Serialize the queryset using DRF serializers
        segment_serializer = MushafSegmentSerializer(mushaf_segments, many=True)
        
        # Return the serialized data in the response
        return Response(segment_serializer.data)
    
class MushafSurahSegmentsView(APIView):
    def get(self, request, mushaf_id):
        # Perform the query and order by category_position
        mushaf_segments = MushafSegment.objects.filter(mushaf_id=mushaf_id, category="surah").order_by('category_position')

        # Serialize the queryset using DRF serializers
        segment_serializer = MushafSegmentSerializer(mushaf_segments, many=True)
        
        # Return the serialized data in the response
        return Response(segment_serializer.data)

class MushafJuzSegmentsView(APIView):
    def get(self, request, mushaf_id):
        # Perform the query and order by category_position
        mushaf_segments = MushafSegment.objects.filter(mushaf_id=mushaf_id, category="juz").order_by('category_position')

        # Serialize the queryset using DRF serializers
        segment_serializer = MushafSegmentSerializer(mushaf_segments, many=True)
        
        # Return the serialized data in the response
        return Response(segment_serializer.data)
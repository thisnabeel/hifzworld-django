from django.urls import path
from .views import MushafSegmentsView, MushafSurahSegmentsView

urlpatterns = [
    path('mushaf_segments', MushafSegmentsView.as_view(), name='mushaf_segments'),
    path('mushafs/<int:mushaf_id>/mushaf_segments', MushafSegmentsView.as_view(), name='mushaf_segments'),

    path('mushafs/<int:mushaf_id>/surahs', MushafSurahSegmentsView.as_view(), name='mushaf_surah_segments'),

]
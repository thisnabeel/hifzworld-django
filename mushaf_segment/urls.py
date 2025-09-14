from django.urls import path
from .views import MushafSegmentsView, MushafSurahSegmentsView, MushafJuzSegmentsView

urlpatterns = [
    path('mushaf_segments', MushafSegmentsView.as_view(), name='mushaf_segments'),
    path('mushafs/<int:mushaf_id>/mushaf_segments', MushafSegmentsView.as_view(), name='mushaf_segments'),

    path('mushafs/<int:mushaf_id>/surahs', MushafSurahSegmentsView.as_view(), name='mushaf_surah_segments'),
    path('mushafs/<int:mushaf_id>/juzs', MushafJuzSegmentsView.as_view(), name='mushaf_juz_segments'),

]
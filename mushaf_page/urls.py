from django.urls import path
from .views import MushafPageDetailView

urlpatterns = [
    path('mushaf_pages/<int:pk>/', MushafPageDetailView.as_view(), name='mushaf_page_detail'),
]

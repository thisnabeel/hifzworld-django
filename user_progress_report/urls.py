from django.urls import path
from .views import UserProgressReportListView

urlpatterns = [
    path('users/<int:user_id>/progress_reports/', UserProgressReportListView.as_view(), name='user-progress-reports'),
]

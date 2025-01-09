from django.urls import path
from .views import StatsView

urlpatterns = [
    path('users/<int:user_id>/stats/', StatsView.as_view(), name='stats'),
]

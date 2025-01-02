from django.urls import path
from . import views

urlpatterns = [
    path('branches/<int:user_id>/', views.get_user_branches, name='get_user_branches'),
]
from django.urls import path
from . import views

app_name = 'user_grants'

urlpatterns = [
    path('', views.UserGrantView.as_view(), name='user_grant'),
    path('revoke/<int:grant_id>/', views.RevokeGrantView.as_view(), name='revoke_grant'),
]
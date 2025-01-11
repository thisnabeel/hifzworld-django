"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from accounts.views import CreateUserView, SignInView, UpdateUserView
from mushaf_page.views import MushafPageView, FindPageByVerseRefView
from user_page.views import UserPageView, CreateUserPageView, UserProgressView, RandomUserPageView
from lead.views import CreateLeadView
from mushaf_segment.views import MushafSegmentsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/sign_up', CreateUserView.as_view(), name='create_user'),
    path('users/sign_in', SignInView.as_view(), name='sign-in'),
    path('mushafs/<int:mushaf_id>/pages/<int:page_number>', MushafPageView.as_view(), name='show_mushaf_page'),   
    path('find_page/<int:mushaf_id>/<str:verse_ref>', FindPageByVerseRefView.as_view(), name='find_page_by_verse_ref_page'),   
    path('users/<int:user_id>/pages/<int:mushaf_page_id>/branch/<int:branch_id>', UserPageView.as_view(), name='show_user_page'),   
    path('user_pages', CreateUserPageView.as_view(), name='create_user_page'),   
    
    path('users/<int:user_id>/progress', UserProgressView.as_view(), name='user_progress'),   
    path('users/<int:user_id>/progress/random/<int:current_page_number>', RandomUserPageView.as_view(), name='user_progress'),   
    path('users/<int:user_id>/update/', UpdateUserView.as_view(), name='update-user'),


    path('leads', CreateLeadView.as_view(), name='create_lead'),
    
    path('', include('mushaf_segment.urls')),  
    path('', include('missions.urls')),
    path('', include('mushaf_page.urls')),
    path('', include('branch.urls')),
    path('', include('stats.urls')),
]

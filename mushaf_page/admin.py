from django.contrib import admin

# Register your models here.
from django.contrib import admin
from mushaf.models import Mushaf
from mushaf_page.models import MushafPage
from django.contrib.auth import get_user_model
from user_page.models import UserPage

admin.site.register(Mushaf)
admin.site.register(MushafPage)
admin.site.register(get_user_model())
admin.site.register(UserPage)
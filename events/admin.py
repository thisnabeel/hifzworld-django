from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'datetime', 'duration', 'unique_code', 'is_private')
    search_fields = ('title', 'user__email', 'unique_code')
    list_filter = ('is_private',)


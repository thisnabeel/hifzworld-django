# models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class UserGrant(models.Model):
    ACCESS_CHOICES = [
        ('granter', 'Granter'),
        ('grantee', 'Grantee'),
    ]
    
    id = models.AutoField(primary_key=True)
    granter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='granted_permissions')
    grantee = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_permissions')
    access_type = models.CharField(max_length=7, choices=ACCESS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('granter', 'grantee')  # Prevent duplicate grants
        
    def clean(self):
        if self.granter == self.grantee:
            raise ValidationError("A user cannot grant access to themselves")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.granter} granted access to {self.grantee}"

# admin.py
from django.contrib import admin
from .models import UserGrant

@admin.register(UserGrant)
class UserGrantAdmin(admin.ModelAdmin):
    list_display = ('granter', 'grantee', 'access_type', 'is_active', 'created_at')
    list_filter = ('access_type', 'is_active', 'created_at')
    search_fields = ('granter__email', 'grantee__email')
    date_hierarchy = 'created_at'

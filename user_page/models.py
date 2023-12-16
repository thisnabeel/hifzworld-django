from django.db import models
from mushaf_page.models import MushafPage 
from django.contrib.auth import get_user_model

class UserPage(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)

    # Foreign key to MushafPage model
    mushaf_page = models.ForeignKey(MushafPage, on_delete=models.CASCADE)

    # Array of dicts (using a JSONField for flexibility)
    drawn_paths = models.JSONField(default=list, null=True)

    # Foreign key to User model
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    camped = models.BooleanField(default=False)

    class Meta:
        app_label = 'user_page'

    def __str__(self):
        return f"UserPage {self.id}"
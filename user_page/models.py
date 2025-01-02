from django.db import models
from mushaf_page.models import MushafPage
from django.contrib.auth import get_user_model
from branch.models import Branch  # Import the Branch model
from django.utils.timezone import now

class UserPage(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)

    # Foreign key to MushafPage model
    mushaf_page = models.ForeignKey(MushafPage, on_delete=models.CASCADE)

    # Array of dicts (using a JSONField for flexibility)
    drawn_paths = models.JSONField(default=list, null=True)

    # Foreign key to User model
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Foreign key to Branch model
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    # Camped status
    camped = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'user_page'

    def __str__(self):
        return f"UserPage {self.id} (Branch: {self.branch.title})"

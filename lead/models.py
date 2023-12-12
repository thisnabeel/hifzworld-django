from django.db import models

class Lead(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)
    # Add other fields as needed
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'lead'

    def __str__(self):
        return f"Lead {self.id}"
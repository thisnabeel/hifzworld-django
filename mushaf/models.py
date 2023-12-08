from django.db import models

class Mushaf(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)
    # Add other fields as needed
    title = models.CharField(max_length=255, default='null')  # Adjust the max length as needed

    class Meta:
        app_label = 'mushaf'

    def __str__(self):
        return f"Mushaf {self.id}"
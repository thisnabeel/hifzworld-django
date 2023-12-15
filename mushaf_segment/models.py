from django.db import models
from mushaf.models import Mushaf

# Create your models here.
class MushafSegment(models.Model):
    # Define the MushafSegment model
    first_page = models.IntegerField()
    last_page = models.IntegerField()
    title = models.CharField(max_length=255)
    mushaf = models.ForeignKey(Mushaf, on_delete=models.CASCADE)  # Assuming a many-to-one relationship
    category = models.CharField(max_length=255)
    category_position = models.IntegerField()

    def __str__(self):
        return self.title  # Adjust this based on how you want to represent the object as a string
    
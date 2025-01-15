from django.db import models
from mushaf.models import Mushaf
from mushaf_page.models import MushafPage

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

def find_mushaf_segment(mushaf_page_id):
    page_number = MushafPage.objects.get(id=mushaf_page_id).page_number
    segment = MushafSegment.objects.filter(
        first_page__lte=page_number,
        last_page__gte=page_number
    ).first()

    return segment
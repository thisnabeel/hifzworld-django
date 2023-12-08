from django.db import models
from mushaf.models import Mushaf  # Import the Mushaf model
from .thirteen_liner_image_urls import IMAGE_URLS  # Import the array
import re

class MushafPage(models.Model):
    # Primary key
    id = models.AutoField(primary_key=True)

    # Add other fields as needed
    page_number = models.IntegerField(default=-1) # Add the page number field
    image_url = models.CharField(max_length=255, default="null")  # Adjust the max length as needed
    mushaf = models.ForeignKey(Mushaf, on_delete=models.CASCADE)  # Adjust on_delete as needed

    class Meta:
        app_label = 'mushaf_page'

    def __str__(self):
        return f"MushafPage {self.id}"

    def create_mushaf_pages(mushaf_id):
        try:
            mushaf = Mushaf.objects.get(id=mushaf_id)  # Ensure the Mushaf object exists
        except Mushaf.DoesNotExist:
            print(f"Mushaf with id {mushaf_id} does not exist.")
            return

        # Delete existing MushafPage objects for the given Mushaf
        MushafPage.objects.filter(mushaf_id=mushaf_id).delete()

        for index, url in enumerate(IMAGE_URLS):
            match = re.search(r'/L(\d+)\.GIF$', url)
            page_number = int(match.group(1))

            MushafPage.objects.create(
                mushaf=mushaf,
                page_number=page_number,
                image_url=url,
            )
            print(page_number, url)

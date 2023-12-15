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
    
    def get_segment_and_percentage(self, page_number):
        try:
            segment = self.mushafsegment_set.get(first_page__lte=page_number, last_page__gte=page_number)
        except:
            return None, 0

        total_pages_in_range = segment.last_page - segment.first_page + 1
        percentage = ((page_number - segment.first_page) / total_pages_in_range) * 100
        rounded_number = round(percentage)

        return segment, rounded_number
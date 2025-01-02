from django.db import models
from django.contrib.auth.models import User
import random
from django.db import IntegrityError
from django.conf import settings


class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    position = models.IntegerField()
    hash_id = models.IntegerField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.hash_id:
            while True:
                # Generate a 4-digit hash_id
                self.hash_id = random.randint(1000, 9999)
                try:
                    super().save(*args, **kwargs)
                    break  # Exit loop if save is successful
                except IntegrityError:
                    # If a duplicate hash_id is generated, retry
                    continue
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Position: {self.position})"

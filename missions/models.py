from django.db import models

class MissionSet(models.Model):
    title = models.CharField(max_length=255)
    position = models.IntegerField()

    def __str__(self):
        return self.title

class Mission(models.Model):
    mission_set = models.ForeignKey(MissionSet, on_delete=models.CASCADE, related_name='missions')
    question = models.TextField()
    verse_ref = models.CharField(max_length=255)
    surah_number = models.IntegerField()
    ayah_number = models.IntegerField()
    position = models.IntegerField()

    def __str__(self):
        return f"{self.mission_set.title} - Mission {self.position}"
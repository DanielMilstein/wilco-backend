from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Clip(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    time_start = models.DateTimeField(null=True)
    time_end = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True)
    date = models.DateField(null=True)
    transcription = models.TextField()
    speaker = models.TextField(null=True)
    score = models.FloatField(null=True)
    keywords = models.TextField(null=True)
    summary = models.TextField(null=True)

    def __str__(self):
        return str(self.id)

from django.db import models
from django.contrib.auth.models import User


class Clip(models.Model):
    clip_id = models.CharField(max_length=255, primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField()
    time_start = models.DateTimeField()
    date = models.DateField()
    transcript = models.TextField()
    entities = models.TextField()
    keywords = models.TextField()
    summary = models.TextField()

    def transcribe_audio(self):
        pass

    def extract_entities(self):
        pass

    def extract_keywords(self):
        pass

    def summarize(self):
        pass

    def __str__(self):
        return f'Clip {self.clip_id} by {self.author}'

    def __repr__(self):
        return f'Clip {self.clip_id} by {self.author}'
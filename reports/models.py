from django.db import models
from clips.models import Clip
from django.contrib.auth.models import User

# Create your models here.

class Report(models.Model):
    title = models.CharField(max_length=100, default='Report')
    audio_clips = models.ManyToManyField('clips.Clip')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.TextField()
    report_objective = models.ForeignKey('ReportObjective', on_delete=models.CASCADE)
    date = models.DateField()



class ReportObjective(models.Model):
    sentence = models.TextField()

    def __str__(self):
        return self.sentence
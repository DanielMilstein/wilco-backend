from rest_framework import serializers
from .models import Clip


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = ['title', 'audio_clips', 'author', 'summary', 'report_objective', 'date']  # Add any other relevant fields




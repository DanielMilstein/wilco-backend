from rest_framework import serializers
from .models import Clip

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = ['user_id', 'transcription', 'summary', 'date', 'time_start', 'time_end', 'duration', 'speaker', 'score']  # Add any other relevant fields

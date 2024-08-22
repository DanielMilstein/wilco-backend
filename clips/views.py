from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Clip
from .serializers import ClipSerializer
from django.shortcuts import render



# Create your views here.
def list_clips(request):
    clips = Clip.objects.all()
    return render(request, 'list_clips.html', {'clips': clips})


def view_clip(request, id):
    clip = Clip.objects.get(pk=id)
    return render(request, 'view_clip.html', {'clip': clip})


@api_view(['POST'])
def create_clip(request):
    if request.method == 'POST':
        serializer = ClipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_clips(request):
    clips = Clip.objects.all()
    serializer = ClipSerializer(clips, many=True)
    return Response(serializer.data)
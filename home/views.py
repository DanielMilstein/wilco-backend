from django.shortcuts import render
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from os import environ
import what3words
from rest_framework.response import Response
import requests
# Create your views here.

API_KEY = '31PTULZ0'
W3W_API_URL = 'https://api.what3words.com/v3/'
geocoder = what3words.Geocoder(API_KEY)

def map(request):
    return render(request, 'what3words_map.html')


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            print("User registered:", user.username)  # Debug: Print username to confirm registration
            return redirect('home')  # Redirect to the home page after registration
        else:
            print("Form errors:", form.errors)  # Debug: Print form errors if validation fails
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})



def get_address(request):
    api_key = API_KEY
    words = request.GET.get('words')
    
    if not words:
        print("NOT WORDS")
        return render(request, 'map.html', {'error': 'Missing required parameter: words'})
    
    try:
        url = 'https://api.what3words.com/v3/convert-to-coordinates?'
        params = {
            'words': words,
            'key': api_key,
            'lang': 'es'
            }
        response = requests.get(url, params=params)
        response_data = response.json()
        print(response_data, "URL")
        print(api_key)

        if 'coordinates' in response_data:
            lat = response_data['coordinates']['lat']
            lon = response_data['coordinates']['lng']
            return render(request, 'map.html', {'latitude': lat, 'longitude': lon})
        else:
            return render(request, 'map.html', {'error': 'Could not find coordinates'})
    except Exception as e:
        return render(request, 'map.html', {'error': str(e)})



def map_view(request):
    # Get coordinates from query parameters
    lat = request.GET.get('lat', 51.505)  # Default to London latitude
    lon = request.GET.get('lon', -0.09)  # Default to London longitude

    context = {
        'latitude': lat,
        'longitude': lon,
    }
    return render(request, 'map.html', context)
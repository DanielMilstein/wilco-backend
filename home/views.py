from django.shortcuts import render
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from clips.models import Clip
from datetime import datetime

SELECTED_DATE = 'SELECTED_DATE'

# Create your views here.
def home(request):
    global SELECTED_DATE

    current_date = datetime.now().date()
    SELECTED_DATE = current_date
    clips = Clip.objects.filter(date=current_date).order_by('-time_start')
    dates = Clip.objects.values('date').distinct()

    return render(request, 'main.html', {'clips': clips, 'current_date': current_date, 'dates': dates})

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

def filter_clips(request):
    global SELECTED_DATE
    SELECTED_DATE = request.GET.get('date')  # Get the date from the request
    SELECTED_DATE = datetime.strptime(SELECTED_DATE, '%d/%m/%Y').date()  # Reformat the date
    clips = Clip.objects.filter(date=SELECTED_DATE).order_by('-time_start')  # Filter clips by the selected date
    return render(request, 'partials/clips_list.html', {'clips': clips})  # Render partial template

def filter_clips2(request):
    global SELECTED_DATE  # Use the global SELECTED_DATE

    # Check if SELECTED_DATE is set and is in the correct format (YYYY-MM-DD)
    if SELECTED_DATE:
        try:
            # Parse the date to ensure it is in the correct format
            SELECTED_DATE = datetime.strptime(str(SELECTED_DATE), '%Y-%m-%d').date()
        except ValueError:
            # Handle the case where the date is not in the correct format
            SELECTED_DATE = datetime.now().date()  # Default to today's date if parsing fails

    # Filter clips by the selected date
    clips = Clip.objects.filter(date=SELECTED_DATE).order_by('-time_start')
    return render(request, 'partials/clips_list.html', {'clips': clips})
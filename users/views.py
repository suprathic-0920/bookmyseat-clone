from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie, Event, Booking

def home(request):
    from movies.models import Theater
    from django.utils import timezone
    
    # City logic
    available_cities = list(Theater.objects.values_list('city', flat=True).distinct().order_by('city'))
    if not available_cities:
        available_cities = ['Madurai', 'Chennai', 'Bengaluru', 'Mumbai', 'Hyderabad']
    
    current_city = request.session.get('city')
    show_city_modal = not current_city
    
    if not current_city or current_city not in available_cities:
        current_city = available_cities[0] if available_cities else 'Chennai'
        request.session['city'] = current_city
    
    # Filter movies that have theaters in the selected city with upcoming shows
    now = timezone.now()
    valid_movie_ids = Theater.objects.filter(city=current_city, time__gte=now).values_list('movie_id', flat=True).distinct()
    movies = Movie.objects.filter(id__in=valid_movie_ids)
    
    # Get all movies for "upcoming" section (not filtered by city)
    upcoming_movies = Movie.objects.all().order_by('-rating')[:10]
    
    events = Event.objects.all()
    return render(request, 'home.html', {
        'movies': movies, 
        'events': events,
        'available_cities': available_cities,
        'current_city': current_city,
        'show_city_modal': show_city_modal,
        'upcoming_movies': upcoming_movies,
    })
def register(request):
    if request.method == 'POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('profile')
    else:
        form=UserRegisterForm()
    return render(request,'users/register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('/')
    else:
        form=AuthenticationForm()
    return render(request,'users/login.html',{'form':form})

@login_required
def profile(request):
    bookings= Booking.objects.filter(user=request.user)
    from movies.models import EventBooking
    event_bookings = EventBooking.objects.filter(user=request.user, payment_status=True).order_by('-booking_time')
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'u_form': u_form,'bookings':bookings, 'event_bookings': event_bookings})

@login_required
def reset_password(request):
    if request.method == 'POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'users/reset_password.html',{'form':form})
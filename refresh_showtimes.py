"""
Refresh all showtimes to be in the future so movies appear as "Now Showing" and are bookable.
This script:
1. Deletes all expired theaters (past showtimes)
2. Creates fresh future showtimes for ALL movies across ALL cities
3. Creates seats for each new showtime
"""
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'bookmyseat.settings'

import django
django.setup()

from movies.models import Movie, Theater, Seat
from django.utils import timezone
from datetime import timedelta
import random

# Configuration
CITIES = ['Chennai', 'Madurai', 'Bengaluru', 'Mumbai', 'Hyderabad']

THEATERS_PER_CITY = {
    'Chennai': [
        'PVR: VR Chennai', 'INOX: Phoenix MarketCity', 'Sathyam Cinemas',
        'SPI: Palazzo', 'AGS Cinemas: T.Nagar', 'Rohini Silver Screens',
        'Kamala Cinemas', 'Udhayam Theatre'
    ],
    'Madurai': [
        'PVR: Vishaal de Mall', 'Meenakshi Theatre', 'Central Theatre',
        'Sri Devi Theatre', 'Anna Theatre', 'Chithirai Theatre'
    ],
    'Bengaluru': [
        'PVR: Orion Mall', 'INOX: Garuda Mall', 'Cinepolis: Royal Meenakshi',
        'PVR: Forum Mall', 'Urvashi Theatre', 'Rex Theatre'
    ],
    'Mumbai': [
        'PVR: Phoenix Palladium', 'INOX: R-City Mall', 'Cinepolis: Viviana Mall',
        'PVR: Juhu', 'Gaiety Galaxy', 'Regal Cinema'
    ],
    'Hyderabad': [
        'PVR: Nexus Mall', 'INOX: GVK One', 'AMB Cinemas',
        'Prasads Multiplex', 'Sudarshan Theatre', 'Asian Mukta Cinemas'
    ],
}

SCREEN_TYPES = ['2D', '3D', 'IMAX', '4K DOLBY ATMOS', 'DOLBY 7.1']

# Seat layout: rows A-J, 12 seats per row = 120 seats
SEAT_ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
SEATS_PER_ROW = 12

def create_seats_for_theater(theater):
    """Create seats for a theater"""
    seats = []
    for row in SEAT_ROWS:
        for num in range(1, SEATS_PER_ROW + 1):
            seats.append(Seat(
                theater=theater,
                seat_number=f'{row}{num}',
                is_booked=False,
                is_locked=False,
            ))
    Seat.objects.bulk_create(seats)

def main():
    movies = Movie.objects.all()
    if not movies.exists():
        print("No movies found in database!")
        return

    now = timezone.now()

    # Step 1: Delete all theaters and their seats (clean slate)
    theaters = Theater.objects.all()
    theater_count = theaters.count()
    print(f"Deleting all {theater_count} existing showtimes to start fresh...")
    theaters.delete()

    # Step 2: Create fresh showtimes for the next 30 days
    print(f"\nCreating fresh showtimes for {movies.count()} movies across {len(CITIES)} cities for the next 30 days...")
    
    created_count = 0
    
    for movie in movies:
        for city in CITIES:
            # Pick 2-3 random theaters in this city
            city_theaters = THEATERS_PER_CITY[city]
            selected_theaters = random.sample(city_theaters, min(3, len(city_theaters)))
            
            for theater_name in selected_theaters:
                # Pick a random screen type
                screen_type = random.choice(SCREEN_TYPES)
                
                # Create shows with a 10-day gap over next 30 days
                for day_offset in range(0, 31, 10):  # Day 0, 10, 20, 30
                    for hour in [10, 14, 18, 21]:  # 10am, 2pm, 6pm, 9pm
                        show_time = now + timedelta(days=day_offset, hours=hour - now.hour, minutes=-now.minute, seconds=-now.second)
                        
                        # Make sure it's in the future
                        if show_time <= now:
                            show_time += timedelta(days=1)
                        
                        theater = Theater.objects.create(
                            name=theater_name,
                            movie=movie,
                            time=show_time,
                            city=city,
                            screen_type=screen_type,
                        )
                        create_seats_for_theater(theater)
                        created_count += 1
    
    print(f"\n[SUCCESS] Created {created_count} new showtimes!")
    print(f"[INFO] Each showtime has {len(SEAT_ROWS) * SEATS_PER_ROW} seats")
    
    # Verify
    future_shows = Theater.objects.filter(time__gte=now).count()
    print(f"\n[STATS] Total future showtimes now: {future_shows}")
    
    for city in CITIES:
        city_count = Theater.objects.filter(city=city, time__gte=now).count()
        movie_count = Movie.objects.filter(
            id__in=Theater.objects.filter(city=city, time__gte=now).values_list('movie_id', flat=True).distinct()
        ).count()
        print(f"   {city}: {city_count} shows, {movie_count} movies live")

if __name__ == '__main__':
    main()

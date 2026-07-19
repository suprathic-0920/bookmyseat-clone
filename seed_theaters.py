"""
Seed Theaters Script — BookMySeat Premium
Seeds real Indian cinema halls across 5 cities with showtimes for the next 7 days.
Run: python seed_theaters.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')

# Setup Django before importing models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from movies.models import Movie, Theater, Seat
from django.utils import timezone
import datetime
import random

# Real Indian cinema halls by city
THEATERS_BY_CITY = {
    'Madurai': [
        {'name': 'Vetri Cinemas (Maattuthavani) Dolby Atmos', 'screen_types': ['LASER DTS X', '4K DOLBY ATMOS', 'LASER ATMOS']},
        {'name': 'Vetri Cinemas (Villapuram) Dolby Atmos', 'screen_types': ['4K DOLBY ATMOS', 'LASER ATMOS']},
        {'name': 'Gopuram Cinemas ATMOS and Laser Projector', 'screen_types': ['LASER ATMOS', '4K ATMOS']},
        {'name': 'Radiance Cinema: Koodal Nagar', 'screen_types': ['2D', 'DOLBY 7.1']},
        {'name': 'Meenakshi Multiplex', 'screen_types': ['2D', '3D']},
    ],
    'Chennai': [
        {'name': 'SPI Palazzo: The Cinema', 'screen_types': ['4K DOLBY ATMOS', 'LASER ATMOS']},
        {'name': 'AGS Cinemas: T.Nagar', 'screen_types': ['4K DOLBY ATMOS', 'LASER DTS X']},
        {'name': 'PVR LUXE: Phoenix Marketcity', 'screen_types': ['IMAX', '4K DOLBY ATMOS', 'LASER ATMOS']},
        {'name': 'Rohini Silver Screens', 'screen_types': ['2D', 'DOLBY 7.1']},
        {'name': 'Sathyam Cinemas', 'screen_types': ['4K DOLBY ATMOS', 'LASER DTS X', 'IMAX']},
    ],
    'Bengaluru': [
        {'name': 'PVR Orion Mall', 'screen_types': ['4K DOLBY ATMOS', 'IMAX']},
        {'name': 'INOX: Mantri Square', 'screen_types': ['LASER ATMOS', '4K ATMOS']},
        {'name': 'Cinepolis: Royal Meenakshi Mall', 'screen_types': ['4K DOLBY ATMOS', '3D']},
    ],
    'Mumbai': [
        {'name': 'PVR IMAX: Phoenix Palladium', 'screen_types': ['IMAX', '4K DOLBY ATMOS']},
        {'name': 'INOX: R City', 'screen_types': ['LASER ATMOS', '4K ATMOS']},
        {'name': 'Cinepolis: Andheri', 'screen_types': ['4K DOLBY ATMOS', 'LASER DTS X']},
    ],
    'Hyderabad': [
        {'name': 'AMB Cinemas', 'screen_types': ['4K DOLBY ATMOS', 'LASER ATMOS', 'IMAX']},
        {'name': 'PVR ICON: Hitech City', 'screen_types': ['4K DOLBY ATMOS', 'LASER DTS X']},
        {'name': 'Prasads Multiplex IMAX', 'screen_types': ['IMAX', '4K DOLBY ATMOS']},
    ],
}

# Showtime slots (hours in 24h format)
SHOWTIME_HOURS = [
    (10, 0),   # 10:00 AM
    (13, 30),  # 1:30 PM
    (16, 45),  # 4:45 PM
    (19, 30),  # 7:30 PM
    (20, 15),  # 8:15 PM
    (22, 30),  # 10:30 PM
    (23, 0),   # 11:00 PM
]


def create_seats_for_theater(theater, num_rows=8, seats_per_row=10):
    """Create seats A1-H10 for a theater."""
    rows = 'ABCDEFGH'[:num_rows]
    seats = []
    for row in rows:
        for num in range(1, seats_per_row + 1):
            seats.append(Seat(
                theater=theater,
                seat_number=f'{row}{num}',
                is_booked=False
            ))
    Seat.objects.bulk_create(seats)


def seed():
    movies = list(Movie.objects.all())
    if not movies:
        print("ERROR: No movies found! Run seed_movies.py first.")
        return

    # Clear existing theaters
    print("Clearing existing theaters and seats...")
    Theater.objects.all().delete()
    Seat.objects.all().delete()

    now = timezone.now()
    today = now.date()
    total_theaters = 0

    for city, theater_list in THEATERS_BY_CITY.items():
        print(f"\n  Seeding theaters for {city}...")
        for theater_info in theater_list:
            theater_name = theater_info['name']
            screen_types = theater_info['screen_types']

            # Each theater shows 2-3 random movies
            selected_movies = random.sample(movies, min(len(movies), random.randint(2, 3)))

            for movie in selected_movies:
                # Create showtimes for next 2 days to keep DB size small for Vercel
                for day_offset in range(2):
                    show_date = today + datetime.timedelta(days=day_offset)

                    # Pick 1 random showtime per day
                    num_shows = 1
                    selected_times = random.sample(SHOWTIME_HOURS, min(len(SHOWTIME_HOURS), num_shows))

                    for hour, minute in selected_times:
                        show_datetime = timezone.make_aware(
                            datetime.datetime.combine(show_date, datetime.time(hour, minute))
                        )

                        # Skip past showtimes for today
                        if show_datetime <= now:
                            continue

                        screen_type = random.choice(screen_types)

                        theater = Theater.objects.create(
                            name=theater_name,
                            movie=movie,
                            time=show_datetime,
                            city=city,
                            screen_type=screen_type
                        )
                        create_seats_for_theater(theater)
                        total_theaters += 1

            print(f"  [OK] {theater_name}")

    print(f"\nDone! Created {total_theaters} theater showtimes across {len(THEATERS_BY_CITY)} cities.")


if __name__ == '__main__':
    seed()

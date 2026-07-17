import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater, Seat

# Theater names common in South India
theater_brands = [
    "PVR Cinemas", 
    "INOX", 
    "Sathyam Cinemas", 
    "AGS Cinemas", 
    "Cinepolis", 
    "Kasi Theatre", 
    "Rohini Silver Screens",
    "Jazz Cinemas",
    "Kamala Cinemas",
    "Mayajaal"
]

movies = Movie.objects.all()

print("Adding multiple theaters for each movie...")

for movie in movies:
    # Pick 2-4 random theater brands for this movie
    brands_to_add = random.sample(theater_brands, k=random.randint(2, 4))
    
    for brand in brands_to_add:
        # Create a new theater for this movie
        theater = Theater.objects.create(
            name=brand,
            movie=movie,
            # Randomize the showtime
            time=timezone.now() + timedelta(days=random.randint(0, 3), hours=random.randint(10, 22), minutes=random.choice([0, 15, 30, 45]))
        )
        
        # Create seats for the theater
        seats = [Seat(theater=theater, seat_number=str(i)) for i in range(1, 21)]
        Seat.objects.bulk_create(seats)

print("✅ Successfully added multiple theaters for every movie!")

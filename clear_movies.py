import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater, Seat

# Deleting all movies will cascade and delete theaters, seats, bookings, and reviews related to them
print(f"Deleting {Movie.objects.count()} existing movies...")
Movie.objects.all().delete()
print("Database cleared of all movies. Ready for fresh import!")

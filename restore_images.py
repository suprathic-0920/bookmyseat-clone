import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie

image_mapping = {
    "Leo": "movies/Leo.jpg",
    "The Dark Knight": "movies/The_Dark_Knight_poster5.webp",
    "Interstellar": "movies/interstellar.jpg",
    "Jailer": "movies/jailer.jpg",
    "KGF Chapter 2": "movies/kgf_2.jpg",
    "Ponniyin Selvan": "movies/ps.jpg",
    "RRR": "movies/rrr.jpg",
    "Vikram": "movies/vikram.jpg"
}

print("Restoring your images...")

for movie_name, image_path in image_mapping.items():
    try:
        movie = Movie.objects.get(name=movie_name)
        movie.image = image_path
        movie.save()
        print(f"Restored image for {movie_name}")
    except Movie.DoesNotExist:
        print(f"Movie {movie_name} not found in DB.")

print("All images restored successfully!")

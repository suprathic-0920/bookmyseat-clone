import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater, Seat, Genre, Language
from django.core.files.base import ContentFile

def seed():
    # Get the existing movie to copy its image
    existing_movie = Movie.objects.first()
    if not existing_movie:
        print("No existing movie found. Please add at least 1 movie via admin first.")
        return

    genres = list(Genre.objects.all())
    languages = list(Language.objects.all())

    if not genres or not languages:
        print("Genres or Languages missing. Run seed_genres first.")
        return

    movie_titles = [
        "The Quantum Paradox", "Echoes of Eternity", "Neon Nights", 
        "Shadows of the Past", "Galactic Drifters", "The Lost Symphony",
        "Crimson Horizon", "Midnight Protocol", "Desert Rose", "Cybernetic Soul",
        "The Last Vanguard", "Whispers in the Wind", "Silent Ascend", 
        "Chronicles of Aethelgard", "Velocity Rush", "The Hidden Realm",
        "Solar Flare", "Abyssal Depths", "Phantom's Revenge", "Celestial Dawn",
        "Iron Resolve", "The Alchemist's Secret", "Beyond the Stars", 
        "Shattered Glass", "The Forgotten King"
    ]

    print("Creating 25 dummy movies...")
    for title in movie_titles:
        movie = Movie.objects.create(
            name=title,
            rating=round(random.uniform(5.0, 10.0), 1),
            cast="John Doe, Jane Smith, Actor Three",
            description=f"An amazing movie about {title}. Full of action, drama, and incredible visual effects.",
            trailer_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        # Reuse image
        if existing_movie.image:
            movie.image = existing_movie.image.name
            movie.save()
            
        # Assign random genres
        assigned_genres = random.sample(genres, random.randint(1, 3))
        movie.genres.set(assigned_genres)
        
        # Assign random languages
        assigned_languages = random.sample(languages, random.randint(1, 3))
        movie.languages.set(assigned_languages)
        
        # Create a theater for the movie
        theater = Theater.objects.create(
            name=f"Cineplex {random.randint(1, 5)}",
            movie=movie,
            time=timezone.now() + timedelta(days=random.randint(1, 7), hours=random.randint(1, 5))
        )
        
        # Create some seats
        seats = []
        for i in range(1, 21):
            seats.append(Seat(theater=theater, seat_number=str(i)))
        Seat.objects.bulk_create(seats)

    print("Successfully created 25 movies with theaters, seats, genres, and languages!")

if __name__ == '__main__':
    seed()

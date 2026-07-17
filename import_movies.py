import os
import django
import csv
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater, Seat, Genre, Language

def import_movies(csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"Error: Could not find {csv_file_path}")
        return

    # Try to grab a default image if available
    default_image = None
    first_movie = Movie.objects.first()
    if first_movie and first_movie.image:
        default_image = first_movie.image.name

    print("Starting Movie Import...\n")
    
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            name = row.get('name', '').strip()
            if not name:
                continue
                
            rating = row.get('rating', '5.0').strip()
            cast = row.get('cast', '').strip()
            description = row.get('description', '').strip()
            trailer_url = row.get('trailer_url', '').strip()
            genres_raw = row.get('genres', '').strip()
            languages_raw = row.get('languages', '').strip()
            
            # 1. Create Movie
            movie = Movie.objects.create(
                name=name,
                rating=float(rating) if rating else 5.0,
                cast=cast,
                description=description,
                trailer_url=trailer_url
            )
            
            if default_image:
                movie.image = default_image
                movie.save()
                
            # 2. Attach Genres
            if genres_raw:
                genre_names = [g.strip() for g in genres_raw.split(',') if g.strip()]
                for g_name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=g_name)
                    movie.genres.add(genre)
                    
            # 3. Attach Languages
            if languages_raw:
                lang_names = [l.strip() for l in languages_raw.split(',') if l.strip()]
                for l_name in lang_names:
                    language, _ = Language.objects.get_or_create(name=l_name)
                    movie.languages.add(language)
                    
            # 4. Create dummy Theater & Seats so it can be booked
            theater = Theater.objects.create(
                name=f"{name} Grand Cinema",
                movie=movie,
                time=timezone.now() + timedelta(days=2)
            )
            seats = [Seat(theater=theater, seat_number=str(i)) for i in range(1, 21)]
            Seat.objects.bulk_create(seats)
            
            print(f"Successfully added: {name}")

    print("\n✅ Movie Import Complete!")

if __name__ == '__main__':
    # Make sure your file is saved as movies_template.csv before running!
    import_movies('movies_template.csv')

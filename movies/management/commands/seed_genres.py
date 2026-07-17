from django.core.management.base import BaseCommand
from movies.models import Movie, Genre, Language
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample Genres and Languages and assigns them to Movies'

    def handle(self, *args, **kwargs):
        genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Animation']
        languages = ['English', 'Hindi', 'Tamil', 'Telugu', 'Malayalam']

        self.stdout.write("Seeding Genres...")
        genre_objs = []
        for g in genres:
            obj, created = Genre.objects.get_or_create(name=g)
            genre_objs.append(obj)
            
        self.stdout.write("Seeding Languages...")
        lang_objs = []
        for l in languages:
            obj, created = Language.objects.get_or_create(name=l)
            lang_objs.append(obj)

        self.stdout.write("Assigning to Movies...")
        movies = Movie.objects.all()
        for movie in movies:
            # Assign 1 to 3 random genres
            assigned_genres = random.sample(genre_objs, random.randint(1, 3))
            movie.genres.set(assigned_genres)
            
            # Assign 1 to 2 random languages
            assigned_languages = random.sample(lang_objs, random.randint(1, 2))
            movie.languages.set(assigned_languages)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded Genres and Languages!'))

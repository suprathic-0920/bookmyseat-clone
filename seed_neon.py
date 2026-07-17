"""
Seed the Neon PostgreSQL database with all data needed for the live website.
This creates: genres, languages, movies, theaters, seats, admin user, and test user.
"""
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'bookmyseat.settings'

import django
django.setup()

from movies.models import Movie, Theater, Seat, Genre, Language
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

def seed_genres_and_languages():
    print("Seeding genres and languages...")
    genre_names = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Adventure']
    for name in genre_names:
        Genre.objects.get_or_create(name=name)
    
    lang_names = ['Tamil', 'English', 'Hindi', 'Telugu', 'Malayalam', 'Kannada']
    for name in lang_names:
        Language.objects.get_or_create(name=name)
    print(f"  Created {len(genre_names)} genres and {len(lang_names)} languages")

def seed_movies():
    print("Seeding movies...")
    genres = list(Genre.objects.all())
    languages = list(Language.objects.all())
    
    movies_data = [
        {"name": "Vikram", "rating": 8.5, "description": "A special agent investigates a case of serial murders.", "image": "movies/vikram.jpg", "cast": "Kamal Haasan, Vijay Sethupathi, Fahadh Faasil"},
        {"name": "Jailer", "rating": 8.2, "description": "A retired jailer goes on a path of vengeance.", "image": "movies/jailer.jpg", "cast": "Rajinikanth, Mohanlal, Jackie Shroff"},
        {"name": "KGF Chapter 2", "rating": 8.4, "description": "Rocky's reign continues as he faces new challenges.", "image": "movies/kgf_2.jpg", "cast": "Yash, Sanjay Dutt, Raveena Tandon"},
        {"name": "RRR", "rating": 8.3, "description": "Two legendary revolutionaries journey away from home.", "image": "movies/rrr.jpg", "cast": "Jr NTR, Ram Charan, Alia Bhatt"},
        {"name": "Ponniyin Selvan", "rating": 7.9, "description": "The epic tale of the Chola dynasty.", "image": "movies/ps.jpg", "cast": "Vikram, Aishwarya Rai, Karthi"},
        {"name": "Master", "rating": 7.8, "description": "An alcoholic professor clashes with a gangster.", "image": "movies/Master.jpg", "cast": "Vijay, Vijay Sethupathi, Malavika Mohanan"},
        {"name": "Soorarai Pottru", "rating": 8.6, "description": "A man with a dream to launch a budget airline.", "image": "movies/Soorarai_Pottru.jpg", "cast": "Suriya, Aparna Balamurali"},
        {"name": "Doctor", "rating": 7.5, "description": "A military doctor tries to save a kidnapped girl.", "image": "movies/doctor.avif", "cast": "Sivakarthikeyan, Priyanka Mohan"},
        {"name": "Leo", "rating": 7.4, "description": "A cafe owner's dark past catches up with him.", "image": "movies/Leo.jpg", "cast": "Vijay, Trisha, Sanjay Dutt"},
        {"name": "GOAT", "rating": 7.6, "description": "The Greatest of All Time - a spy thriller.", "image": "movies/GOAT_The_Greatest_of_All_Time.jpg", "cast": "Vijay, Prashanth, Prabhu Deva"},
        {"name": "Petta", "rating": 7.7, "description": "A hostel warden with a mysterious past.", "image": "movies/Petta.jpg", "cast": "Rajinikanth, Vijay Sethupathi, Nawazuddin"},
        {"name": "Mankatha", "rating": 7.8, "description": "A suspended cop plans the heist of a lifetime.", "image": "movies/Mankatha.jpg", "cast": "Ajith Kumar, Arjun, Trisha"},
        {"name": "Theri", "rating": 7.6, "description": "A police officer goes undercover to protect his daughter.", "image": "movies/Theri.jpg", "cast": "Vijay, Samantha, Amy Jackson"},
        {"name": "Kaithi", "rating": 8.3, "description": "An ex-convict tries to meet his daughter for the first time.", "image": "movies/Kaithi.jpg", "cast": "Karthi, Narain, George Maryan"},
        {"name": "Maharaja", "rating": 8.1, "description": "A barber seeks justice through unconventional means.", "image": "movies/Maharaja.jpg", "cast": "Vijay Sethupathi, Anurag Kashyap"},
        {"name": "Interstellar", "rating": 8.7, "description": "A team of explorers travel through a wormhole in space.", "image": "movies/interstellar.jpg", "cast": "Matthew McConaughey, Anne Hathaway"},
        {"name": "The Dark Knight", "rating": 9.0, "description": "Batman faces the Joker, a criminal mastermind.", "image": "movies/The_Dark_Knight_poster5.webp", "cast": "Christian Bale, Heath Ledger"},
        {"name": "Thunivu", "rating": 7.2, "description": "A heist thriller with unexpected twists.", "image": "movies/Thunivu.jpg", "cast": "Ajith Kumar, Manju Warrier"},
        {"name": "Valimai", "rating": 6.8, "description": "A cop takes on a gang of bikers.", "image": "movies/Valimai.jpg", "cast": "Ajith Kumar, Huma Qureshi"},
        {"name": "Raayan", "rating": 7.5, "description": "A man protects his family at all costs.", "image": "movies/Raayan.jpg", "cast": "Dhanush, SJ Suryah, Prakash Raj"},
        {"name": "Vettaiyan", "rating": 7.3, "description": "A police officer deals with encounter killings.", "image": "movies/Vettaiyan.jpg", "cast": "Rajinikanth, Amitabh Bachchan"},
        {"name": "Enthiran", "rating": 7.9, "description": "A scientist creates a humanoid robot.", "image": "movies/Enthiran.jpg", "cast": "Rajinikanth, Aishwarya Rai"},
        {"name": "Sivaji", "rating": 7.8, "description": "An NRI fights corruption in the system.", "image": "movies/Sivaji.jpg", "cast": "Rajinikanth, Shriya Saran"},
        {"name": "Viswasam", "rating": 7.1, "description": "A village chieftain protects his daughter.", "image": "movies/Viswasam.jpg", "cast": "Ajith Kumar, Nayanthara"},
        {"name": "Kanguva", "rating": 6.9, "description": "A warrior from the past battles in the present.", "image": "movies/Kanguva.jpg", "cast": "Suriya, Bobby Deol, Disha Patani"},
        {"name": "Indian 2", "rating": 6.5, "description": "Senapathy returns to fight corruption.", "image": "movies/Indian_2.jpg", "cast": "Kamal Haasan, Siddharth"},
        {"name": "Maaveeran", "rating": 7.4, "description": "A timid man gains superpowers from a comic book.", "image": "movies/Maaveeran.jpg", "cast": "Sivakarthikeyan, Aditi Shankar"},
        {"name": "Meiyazhagan", "rating": 7.8, "description": "A heartwarming tale of reconnecting with the past.", "image": "movies/Meiyazhagan.jpg", "cast": "Karthi, Arvind Swamy"},
        {"name": "Thiruchitrambalam", "rating": 7.6, "description": "A delivery boy navigates love and family.", "image": "movies/Thiruchitrambalam.jpg", "cast": "Dhanush, Nithya Menen"},
        {"name": "Pariyerum Perumal", "rating": 8.5, "description": "A law student fights caste discrimination.", "image": "movies/pariyerum_perumal.jpg", "cast": "Kathir, Anandhi"},
    ]
    
    created = 0
    for m in movies_data:
        movie, was_created = Movie.objects.get_or_create(
            name=m["name"],
            defaults={
                "rating": m["rating"],
                "description": m["description"],
                "image": m["image"],
                "cast": m["cast"],
            }
        )
        if was_created:
            movie.genres.add(*random.sample(genres, min(3, len(genres))))
            movie.languages.add(*random.sample(languages, min(2, len(languages))))
            created += 1
    print(f"  Created {created} movies (total: {Movie.objects.count()})")

def seed_theaters():
    print("Seeding theaters with 10-day gap showtimes...")
    movies = list(Movie.objects.all())
    now = timezone.now()
    
    CITIES = ['Chennai', 'Madurai', 'Bengaluru', 'Mumbai', 'Hyderabad']
    THEATERS_PER_CITY = {
        'Chennai': ['PVR: VR Chennai', 'Sathyam Cinemas', 'Rohini Silver Screens', 'AGS Cinemas'],
        'Madurai': ['PVR: Vishaal de Mall', 'Meenakshi Theatre', 'Central Theatre'],
        'Bengaluru': ['PVR: Orion Mall', 'INOX: Garuda Mall', 'Cinepolis: Royal Meenakshi'],
        'Mumbai': ['PVR: Phoenix Palladium', 'INOX: R-City Mall', 'Gaiety Galaxy'],
        'Hyderabad': ['PVR: Nexus Mall', 'INOX: GVK One', 'AMB Cinemas'],
    }
    SCREEN_TYPES = ['2D', '3D', 'IMAX', '4K DOLBY ATMOS', 'DOLBY 7.1']
    SHOW_TIMES = [10, 14, 18, 21]  # 10am, 2pm, 6pm, 9pm
    
    total_theaters = 0
    total_seats = 0
    
    # Create shows at day 0, 10, 20, 30
    for day_offset in [0, 10, 20, 30]:
        show_date = now + timedelta(days=day_offset)
        
        for city, theater_names in THEATERS_PER_CITY.items():
            for theater_name in theater_names:
                # Each theater shows 3 random movies
                selected_movies = random.sample(movies, min(3, len(movies)))
                
                for movie in selected_movies:
                    for hour in random.sample(SHOW_TIMES, 2):  # 2 showtimes per movie
                        showtime = show_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                        if showtime < now:
                            showtime += timedelta(days=1)
                        
                        screen = random.choice(SCREEN_TYPES)
                        
                        theater = Theater.objects.create(
                            movie=movie,
                            name=f"{theater_name} - Screen {random.randint(1,5)}",
                            time=showtime,
                            city=city,
                            screen_type=screen,
                        )
                        total_theaters += 1
                        
                        # Create 120 seats
                        seats = []
                        rows = 'ABCDEFGHIJ'
                        for row in rows:
                            for num in range(1, 13):
                                seats.append(Seat(
                                    theater=theater,
                                    seat_number=f"{row}{num}",
                                    is_booked=False,
                                ))
                        Seat.objects.bulk_create(seats)
                        total_seats += len(seats)
    
    print(f"  Created {total_theaters} showtimes with {total_seats} seats")

def seed_users():
    print("Seeding users...")
    # Admin user
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@bookmyseat.com', 'admin123')
        print("  Created admin user (admin / admin123)")
    
    # Test user
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user('testuser', 'testuser@bookmyseat.com', 'test1234')
        user.first_name = 'Test'
        user.last_name = 'User'
        user.save()
        print("  Created test user (testuser / test1234)")

def main():
    print("=" * 50)
    print("Seeding Neon PostgreSQL Database")
    print("=" * 50)
    seed_genres_and_languages()
    seed_movies()
    seed_theaters()
    seed_users()
    print("=" * 50)
    print("DONE! Database is ready.")
    print("=" * 50)

if __name__ == '__main__':
    main()

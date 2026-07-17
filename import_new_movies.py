import os
import django
import csv
from datetime import timedelta
from django.utils import timezone
import random
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Movie, Theater, Seat, Genre, Language

csv_data = """name,rating,cast,description,trailer_url,genres,languages
"Master","7.8","Vijay, Vijay Sethupathi, Malavika Mohanan","An alcoholic professor is sent to a juvenile school, where he clashes with a gangster who uses the children for criminal activities.","https://www.youtube.com/watch?v=UTiXQcrLlv4","Action, Thriller","Tamil, Telugu, Hindi, Malayalam"
"Doctor","7.4","Sivakarthikeyan, Vinay Rai, Priyanka Arul Mohan","A military doctor goes after a human trafficking gang to rescue his ex-fiancee's niece.","https://www.youtube.com/watch?v=oQiH_Iw0kDs","Action, Comedy","Tamil, Telugu, Malayalam"
"Karnan","8.1","Dhanush, Lal, Rajisha Vijayan","A fearless village youth fights for the rights of his oppressed people against a powerful local politician.","https://www.youtube.com/watch?v=HkQp2xN8rFw","Action, Drama","Tamil, Telugu"
"Maanaadu","8.3","Silambarasan, S. J. Suryah, Kalyani Priyadarshan","A man and a police officer get trapped in a time loop on the day of the Chief Minister's public rally.","https://www.youtube.com/watch?v=t9OqtRIrtkQ","Sci-Fi, Action, Thriller","Tamil, Telugu, Hindi"
"Thiruchitrambalam","7.9","Dhanush, Nithya Menen, Raashii Khanna","A delivery boy navigates his complicated love life and family relationships with the help of his childhood best friend.","https://www.youtube.com/watch?v=sMIEvB0B5pQ","Romance, Comedy, Drama","Tamil, Telugu"
"Love Today","8.1","Pradeep Ranganathan, Ivana, Yogi Babu","Two young lovers are forced to exchange their phones for a day by the girl's father, leading to chaotic revelations.","https://www.youtube.com/watch?v=O15N5L3p6Lg","Romance, Comedy","Tamil, Telugu, Hindi"
"Varisu","6.0","Vijay, Rashmika Mandanna, Sarathkumar","The youngest son of a business tycoon is forced to take over the family empire and reunite his broken family.","https://www.youtube.com/watch?v=9fNXE28K0zU","Action, Drama","Tamil, Telugu, Hindi, Malayalam"
"Thunivu","6.1","Ajith Kumar, Manju Warrier, Samuthirakani","A mysterious mastermind and his team hijack a bank, but their motives go far beyond a simple robbery.","https://www.youtube.com/watch?v=jn5G327bZ90","Action, Thriller","Tamil, Telugu, Hindi"
"Maharaja","8.6","Vijay Sethupathi, Anurag Kashyap, Mamta Mohandas","A barber seeks revenge after his house is burglarized, telling a puzzling story about a missing dustbin.","https://www.youtube.com/watch?v=kYpuBvQ7Uoo","Action, Thriller","Tamil, Telugu, Hindi"
"Viduthalai Part 1","8.4","Soori, Vijay Sethupathi, Bhavani Sre","A newly recruited police constable is caught between his duty and his moral conscience during a hunt for a rebel leader.","https://www.youtube.com/watch?v=0kFhyjUa14Q","Crime, Drama, Thriller","Tamil, Telugu"
"""

theater_brands = [
    "PVR Cinemas", "INOX", "Sathyam Cinemas", "AGS Cinemas", 
    "Cinepolis", "Kasi Theatre", "Rohini Silver Screens",
    "Jazz Cinemas", "Kamala Cinemas", "Mayajaal"
]

reader = csv.DictReader(io.StringIO(csv_data))

first_movie = Movie.objects.first()
default_image = first_movie.image.name if first_movie and first_movie.image else None

for row in reader:
    name = row['name']
    movie, created = Movie.objects.get_or_create(
        name=name,
        defaults={
            'rating': float(row['rating']),
            'cast': row['cast'],
            'description': row['description'],
            'trailer_url': row['trailer_url']
        }
    )
    
    if not created:
        print(f"Skipping {name}, already exists.")
        continue
        
    if default_image:
        movie.image = default_image
        movie.save()
        
    for g_name in [g.strip() for g in row['genres'].split(',')]:
        genre, _ = Genre.objects.get_or_create(name=g_name)
        movie.genres.add(genre)
        
    for l_name in [l.strip() for l in row['languages'].split(',')]:
        language, _ = Language.objects.get_or_create(name=l_name)
        movie.languages.add(language)
        
    # Add theaters
    brands_to_add = random.sample(theater_brands, k=random.randint(2, 4))
    for brand in brands_to_add:
        theater = Theater.objects.create(
            name=brand,
            movie=movie,
            time=timezone.now() + timedelta(days=random.randint(0, 3), hours=random.randint(10, 22), minutes=random.choice([0, 15, 30, 45]))
        )
        seats = [Seat(theater=theater, seat_number=str(i)) for i in range(1, 21)]
        Seat.objects.bulk_create(seats)
        
    print(f"Successfully added: {name} with theaters!")
    
print("All 10 new movies imported successfully!")

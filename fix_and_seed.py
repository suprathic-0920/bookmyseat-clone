import os
import django
from django.utils import timezone
import random

# 1. Fix template inheritance
template_files = [
    os.path.join('templates', 'movies', 'event_list.html'),
    os.path.join('templates', 'movies', 'event_detail.html'),
    os.path.join('templates', 'movies', 'event_payment_success.html')
]

for file_path in template_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("{% extends 'base.html' %}", '{% extends "users/basic.html" %}')
        content = content.replace('{% extends "base.html" %}', '{% extends "users/basic.html" %}')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_path}")

# 2. Seed 4 events for each category
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Event

categories = {
    'Comedy': [
        "Zakir Khan Live", "Vir Das: Mind Fool Tour", "Trevor Noah - Off The Record", "Russell Peters - Act Your Age"
    ],
    'Music': [
        "A.R. Rahman Live Concert", "Coldplay: Music of the Spheres", "Ed Sheeran: Mathematics Tour", "Taylor Swift: The Eras Tour"
    ],
    'Workshop': [  # Mapped to Theatre Plays
        "Hamilton", "The Phantom of the Opera", "Harry Potter and the Cursed Child", "Wicked - The Musical"
    ],
    'Sports': [
        "IPL Final Screening", "FIFA World Cup Finals", "Wimbledon Men's Final", "UFC 300 Live Screening"
    ]
}

venues = ["Wembley Stadium", "Madison Square Garden", "O2 Arena", "Sydney Opera House", "Jio World Centre", "Royal Albert Hall"]

for cat_code, event_names in categories.items():
    for name in event_names:
        if not Event.objects.filter(name=name).exists():
            Event.objects.create(
                name=name,
                description=f"Experience the thrill of {name} live and exclusive. Book your tickets now before they sell out!",
                category=cat_code,
                venue=random.choice(venues),
                date_time=timezone.now() + timezone.timedelta(days=random.randint(5, 60)),
                ticket_price=round(random.uniform(50.0, 500.0), 2),
                total_tickets=1000,
                available_tickets=1000
            )

print("Seeded 4 events for every category!")

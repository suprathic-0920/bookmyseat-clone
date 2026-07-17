import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Event

if not Event.objects.filter(name="A.R. Rahman Live Concert").exists():
    Event.objects.create(
        name="A.R. Rahman Live Concert",
        description="Experience the magic of A.R. Rahman live in concert. A night of soulful music and electrifying performances featuring his greatest hits from the last 2 decades.",
        category="Music",
        venue="Wembley Stadium, London",
        date_time=timezone.now() + timezone.timedelta(days=10),
        ticket_price=150.00,
        total_tickets=5000,
        available_tickets=5000
    )
    print("Test event created successfully!")
else:
    print("Test event already exists.")

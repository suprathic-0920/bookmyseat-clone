import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Event

if not Event.objects.filter(name="Oppenheimer - Director's Cut").exists():
    Event.objects.create(
        name="Oppenheimer - Director's Cut",
        description="Exclusive digital premiere of the legendary director's cut.",
        category="Premiere",
        venue="Digital Online Premiere",
        date_time=timezone.now() + timezone.timedelta(days=2),
        ticket_price=15.00,
        total_tickets=10000,
        available_tickets=10000
    )

if not Event.objects.filter(name="Anirudh Live Session").exists():
    Event.objects.create(
        name="Anirudh Live Session",
        description="Join Anirudh live in the studio for an exclusive unplugged session.",
        category="Studio",
        venue="BookMyShow Studio Online",
        date_time=timezone.now() + timezone.timedelta(days=5),
        ticket_price=10.00,
        total_tickets=5000,
        available_tickets=5000
    )

print("Seed completed!")

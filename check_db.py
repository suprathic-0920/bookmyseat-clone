import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Seat

print("--- SEATS 1 AND 2 ---")
seats = Seat.objects.filter(id__in=[1, 2])
for s in seats:
    print(f"ID: {s.id}, Seat: {s.seat_number}, Locked: {s.is_locked}, Booked: {s.is_booked}")

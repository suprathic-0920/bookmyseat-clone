import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Payment, Booking

payments = Payment.objects.order_by('-created_at')[:3]
print("--- RECENT PAYMENTS ---")
for p in payments:
    print(f"ID: {p.id}, Checkout ID: {p.stripe_checkout_id}, Status: {p.status}, Created: {p.created_at}")

bookings = Booking.objects.order_by('-id')[:3]
print("\n--- RECENT BOOKINGS ---")
for b in bookings:
    print(f"ID: {b.id}, Movie: {b.movie.name}, User: {b.user.username}, Seat: {b.seat.seat_number}")
    

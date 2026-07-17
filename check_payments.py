import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Payment, EventBooking

print("--- Movie Payments ---")
for p in Payment.objects.all().order_by('-created_at')[:5]:
    print(f"ID: {p.id}, User: {p.user.username}, Amount: {p.amount}, Status: {p.status}, Stripe ID: {p.stripe_checkout_id}")

print("\n--- Event Bookings ---")
for e in EventBooking.objects.all().order_by('-booking_time')[:5]:
    print(f"ID: {e.id}, User: {e.user.username}, Amount: {e.total_amount}, Payment Status: {e.payment_status}, Stripe ID: {e.stripe_checkout_id}")

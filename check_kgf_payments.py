import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Payment, Booking

print("--- Recent Payments ---")
payments = Payment.objects.all().order_by('-created_at')[:10]
for p in payments:
    print(f"ID: {p.id}, User: {p.user.username}, Movie: {p.theater.movie.name}, Amount: {p.amount}, Status: {p.status}, Stripe ID: {p.stripe_checkout_id}")

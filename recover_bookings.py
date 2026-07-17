import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import Payment, Booking, Seat, FoodItem, BookingFoodItem
from movies.tasks import send_ticket_email
import json

recovered_count = 0

payments = Payment.objects.filter(status='SUCCESS')
for payment in payments:
    booking_data = payment.seat_ids
    if isinstance(booking_data, dict) and "seats" in booking_data:
        actual_seat_ids = booking_data["seats"]
        food_dict = booking_data.get("food", {})
    else:
        if isinstance(booking_data, str):
            try:
                booking_data = json.loads(booking_data)
                if isinstance(booking_data, dict) and "seats" in booking_data:
                    actual_seat_ids = booking_data["seats"]
                    food_dict = booking_data.get("food", {})
                else:
                    actual_seat_ids = booking_data
                    food_dict = {}
            except:
                actual_seat_ids = booking_data
                food_dict = {}
        else:
            actual_seat_ids = booking_data
            food_dict = {}

    if not isinstance(actual_seat_ids, list):
        continue

    # Check if bookings exist for this payment's seats and user
    existing_bookings = Booking.objects.filter(user=payment.user, seat__id__in=actual_seat_ids)
    if existing_bookings.count() < len(actual_seat_ids):
        # We need to recover!
        seats = Seat.objects.filter(id__in=actual_seat_ids)
        booking_ids = []
        for seat in seats:
            if not Booking.objects.filter(user=payment.user, seat=seat).exists():
                booking = Booking.objects.create(
                    user=payment.user,
                    seat=seat,
                    movie=payment.theater.movie,
                    theater=payment.theater
                )
                booking_ids.append(booking.id)
                
                # Add food
                for food_id, quantity in food_dict.items():
                    try:
                        food_item = FoodItem.objects.get(id=int(food_id))
                        BookingFoodItem.objects.create(
                            booking=booking, 
                            food_item=food_item, 
                            quantity=quantity
                        )
                    except:
                        pass
                
                seat.is_booked = True
                seat.is_locked = False
                seat.locked_by = None
                seat.locked_until = None
                seat.save()
                recovered_count += 1
                
        if booking_ids:
            try:
                send_ticket_email(booking_ids, payment.stripe_checkout_id)
            except:
                pass

print(f"Recovered {recovered_count} bookings!")

import os
import re

views_path = os.path.join('movies', 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Replace payment_success
old_success = """@login_required(login_url='/login/')
def payment_success(request):
    # Removing this to prevent Django SessionInterrupted errors on SQLite concurrent writes
    # if 'pending_booking' in request.session:
    #     del request.session['pending_booking']
    return render(request, 'movies/payment_success.html')"""

new_success = """@login_required(login_url='/login/')
def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                payment = Payment.objects.get(stripe_checkout_id=session_id)
                if payment.status == 'PENDING':
                    # Webhook missed it, process manually
                    from django.db import transaction
                    from .models import Seat, Booking, BookingFoodItem, FoodItem
                    from .tasks import send_ticket_email
                    import json
                    
                    with transaction.atomic():
                        payment.status = 'SUCCESS'
                        payment.save()
                        
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
                                
                        if booking_ids:
                            try:
                                send_ticket_email(booking_ids, session_id)
                            except:
                                pass
        except Exception as e:
            pass
            
    return render(request, 'movies/payment_success.html')"""

# Replace event_payment_success
old_event_success = """@login_required(login_url='/login/')
def event_payment_success(request):
    return render(request, 'movies/event_payment_success.html')"""

new_event_success = """@login_required(login_url='/login/')
def event_payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                from .models import EventBooking
                event_booking = EventBooking.objects.get(stripe_checkout_id=session_id)
                if not event_booking.payment_status:
                    # Webhook missed it, process manually
                    event_booking.payment_status = True
                    event_booking.save()
                    event_booking.event.available_tickets -= event_booking.tickets_count
                    event_booking.event.save()
        except Exception as e:
            pass
            
    return render(request, 'movies/event_payment_success.html')"""

if old_success in views_content:
    views_content = views_content.replace(old_success, new_success)
if old_event_success in views_content:
    views_content = views_content.replace(old_event_success, new_event_success)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)

print("Upgraded success views to sync with Stripe directly!")

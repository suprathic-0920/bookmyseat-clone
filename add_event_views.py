import os

views_path = r"c:\Users\supra\Downloads\djnago-bookmyshow-clone\movies\views.py"

with open(views_path, "r", encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "from .models import Movie, Theater, Seat, Payment, Booking",
    "from .models import Movie, Theater, Seat, Payment, Booking, Event, EventBooking"
)

# 2. Add event views at the end of the file
new_views = """

@login_required(login_url='/login/')
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'movies/event_detail.html', {'event': event})

@login_required(login_url='/login/')
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        tickets_count = int(request.POST.get('tickets_count', 1))
        
        if event.available_tickets < tickets_count:
            messages.error(request, "Not enough tickets available.")
            return redirect('event_detail', event_id=event.id)
            
        total_amount = event.ticket_price * tickets_count
        
        booking = EventBooking.objects.create(
            user=request.user,
            event=event,
            tickets_count=tickets_count,
            total_amount=total_amount,
            payment_status=False
        )
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        domain_url = request.build_absolute_uri('/')[:-1]
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"{tickets_count}x Tickets for {event.name}",
                            },
                            'unit_amount': int(total_amount * 100),
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=domain_url + f'/movies/event/payment/success/?booking_id={booking.id}',
                cancel_url=domain_url + f'/movies/event/{event.id}/',
                client_reference_id=request.user.id,
            )
            booking.stripe_checkout_id = checkout_session.id
            booking.save()
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('event_detail', event_id=event.id)
            
    return redirect('event_detail', event_id=event.id)

@login_required(login_url='/login/')
def event_payment_success(request):
    booking_id = request.GET.get('booking_id')
    if booking_id:
        booking = get_object_or_404(EventBooking, id=booking_id, user=request.user)
        if not booking.payment_status:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                session = stripe.checkout.Session.retrieve(booking.stripe_checkout_id)
                if session.payment_status == 'paid':
                    booking.payment_status = True
                    booking.save()
                    booking.event.available_tickets -= booking.tickets_count
                    booking.event.save()
            except Exception as e:
                pass
        return render(request, 'movies/event_payment_success.html', {'booking': booking})
    return redirect('home')
"""

if "def event_detail(" not in content:
    content += new_views

# 3. Update webhook to also handle EventBooking
webhook_find = """        try:
            payment = Payment.objects.get(stripe_checkout_id=session['id'])
        except Payment.DoesNotExist:"""

webhook_replace = """        try:
            payment = Payment.objects.get(stripe_checkout_id=session['id'])
        except Payment.DoesNotExist:
            try:
                event_booking = EventBooking.objects.get(stripe_checkout_id=session['id'])
                if not event_booking.payment_status:
                    event_booking.payment_status = True
                    event_booking.save()
                    event_booking.event.available_tickets -= event_booking.tickets_count
                    event_booking.event.save()
                return HttpResponse(status=200)
            except EventBooking.DoesNotExist:
                return HttpResponse(status=400)"""

content = content.replace(webhook_find, webhook_replace)

with open(views_path, "w", encoding='utf-8') as f:
    f.write(content)

print("movies/views.py successfully updated!")

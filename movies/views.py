from django.shortcuts import render, redirect ,get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Theater, Seat, Booking, Payment, Genre, Language, Event, EventBooking
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction, OperationalError
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, ExtractHour
from django.utils import timezone
from django.core.cache import cache
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
except ImportError:
    get_channel_layer = None
    async_to_sync = None
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from xhtml2pdf import pisa
import datetime
import logging
import stripe
import uuid
import json
from .tasks import unlock_seats, send_ticket_email

logger = logging.getLogger(__name__)

def set_city(request):
    if request.method == 'POST':
        # Handle both form POST and AJAX JSON
        content_type = request.content_type or ''
        if 'application/json' in content_type:
            try:
                data = json.loads(request.body)
                city = data.get('city')
            except (json.JSONDecodeError, Exception):
                city = None
        else:
            city = request.POST.get('city')
        if city:
            request.session['city'] = city
            if 'application/json' in content_type:
                return JsonResponse({'status': 'ok', 'city': city})
    return redirect(request.META.get('HTTP_REFERER', '/'))


def detect_city_api(request):
    """API endpoint to detect city from GPS coordinates using reverse geocoding mapping."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = float(data.get('lat', 0))
            lng = float(data.get('lng', 0))
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)

        # Indian city coordinate mapping (approximate bounding boxes)
        CITY_COORDS = {
            'Madurai': {'lat': 9.9252, 'lng': 78.1198, 'radius': 0.5},
            'Chennai': {'lat': 13.0827, 'lng': 80.2707, 'radius': 0.6},
            'Bengaluru': {'lat': 12.9716, 'lng': 77.5946, 'radius': 0.6},
            'Mumbai': {'lat': 19.0760, 'lng': 72.8777, 'radius': 0.7},
            'Hyderabad': {'lat': 17.3850, 'lng': 78.4867, 'radius': 0.6},
            'Delhi-NCR': {'lat': 28.6139, 'lng': 77.2090, 'radius': 0.8},
            'Pune': {'lat': 18.5204, 'lng': 73.8567, 'radius': 0.5},
            'Kolkata': {'lat': 22.5726, 'lng': 88.3639, 'radius': 0.6},
            'Kochi': {'lat': 9.9312, 'lng': 76.2673, 'radius': 0.4},
            'Coimbatore': {'lat': 11.0168, 'lng': 76.9558, 'radius': 0.4},
        }

        # Find nearest city
        nearest_city = None
        min_distance = float('inf')
        for city_name, coords in CITY_COORDS.items():
            distance = ((lat - coords['lat']) ** 2 + (lng - coords['lng']) ** 2) ** 0.5
            if distance < coords['radius'] and distance < min_distance:
                min_distance = distance
                nearest_city = city_name

        # Get available cities from DB
        available_cities = list(Theater.objects.values_list('city', flat=True).distinct().order_by('city'))

        if nearest_city and nearest_city in available_cities:
            request.session['city'] = nearest_city
            return JsonResponse({'status': 'ok', 'city': nearest_city, 'available_cities': available_cities})
        elif nearest_city:
            # City detected but not in DB, fallback to nearest available
            return JsonResponse({'status': 'ok', 'city': nearest_city, 'detected': True, 'available_cities': available_cities,
                                 'message': f'{nearest_city} detected but no theaters available. Please select a city.'})
        else:
            return JsonResponse({'status': 'not_found', 'available_cities': available_cities,
                                 'message': 'Could not detect your city. Please select manually.'})

    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


def get_cities_api(request):
    """API endpoint returning list of all cities with theaters."""
    available_cities = list(Theater.objects.values_list('city', flat=True).distinct().order_by('city'))
    if not available_cities:
        available_cities = ['Madurai', 'Chennai', 'Bengaluru', 'Mumbai', 'Hyderabad']
    return JsonResponse({'cities': available_cities})

def movie_list(request):
    movies = Movie.objects.all()

    # Get current city from session or default
    from .models import Theater
    available_cities = list(Theater.objects.values_list('city', flat=True).distinct().order_by('city'))
    if not available_cities:
        available_cities = ['Madurai', 'Chennai']
        
    current_city = request.session.get('city')
    if not current_city or current_city not in available_cities:
        current_city = available_cities[0]
        request.session['city'] = current_city
        
    # Filter movies by the current city (must have at least one future/current theater in that city)
    now = timezone.now()
    valid_movie_ids = Theater.objects.filter(city=current_city, time__gte=now).values_list('movie_id', flat=True).distinct()
    movies = movies.filter(id__in=valid_movie_ids)

    # 1. Capture query parameters
    search_query = request.GET.get('search', '')
    selected_genres = request.GET.getlist('genre')
    selected_languages = request.GET.getlist('language')
    sort_by = request.GET.get('sort', '-rating')

    # 2. Apply text search
    if search_query:
        movies = movies.filter(name__icontains=search_query)

    # 3. Apply Multi-Select Genre Filter
    if selected_genres:
        movies = movies.filter(genres__id__in=selected_genres)

    # 4. Apply Multi-Select Language Filter
    if selected_languages:
        movies = movies.filter(languages__id__in=selected_languages)

    # Prevent duplicates from ManyToMany joins
    movies = movies.distinct()

    # 5. Dynamic Aggregation: Calculate exact counts of movies available 
    # under each genre/language *after* the current filters are applied.
    # This fulfills the optimization requirement and provides a faceted search experience.
    genres = Genre.objects.annotate(
        movie_count=Count('movies', filter=Q(movies__in=movies))
    ).filter(movie_count__gt=0).order_by('-movie_count')

    languages = Language.objects.annotate(
        movie_count=Count('movies', filter=Q(movies__in=movies))
    ).filter(movie_count__gt=0).order_by('-movie_count')

    # 6. Apply Sorting (Leverages db_index=True on rating)
    if sort_by == 'rating':
        movies = movies.order_by('rating')
    elif sort_by == '-rating':
        movies = movies.order_by('-rating')
    elif sort_by == 'name':
        movies = movies.order_by('name')
    elif sort_by == '-name':
        movies = movies.order_by('-name')
    else:
        movies = movies.order_by('-rating')

    # 7. Server-Side Pagination
    # Optimized to limit the dataset before it hits memory
    paginator = Paginator(movies, 9) # 9 movies per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_genres': [int(i) for i in selected_genres if i.isdigit()],
        'selected_languages': [int(i) for i in selected_languages if i.isdigit()],
        'sort_by': sort_by,
        'genres': genres,
        'languages': languages,
        'available_cities': available_cities,
        'current_city': current_city
    }
    return render(request, 'movies/movie_list.html', context)

def theater_list(request, movie_id):
    from .models import Review
    from django.utils import timezone
    import datetime
    
    movie = get_object_or_404(Movie, id=movie_id)
    now = timezone.now()
    
    # Get current city from session
    from .models import Theater
    available_cities = list(Theater.objects.values_list('city', flat=True).distinct().order_by('city'))
    selected_city = request.session.get('city')
    if not selected_city or selected_city not in available_cities:
        selected_city = available_cities[0] if available_cities else 'Madurai'
        request.session['city'] = selected_city
        
    all_theaters = Theater.objects.filter(movie=movie, time__gte=now, city=selected_city)
    
    available_dates = []
    for t in all_theaters:
        d = t.time.date()
        if d not in available_dates:
            available_dates.append(d)
    available_dates.sort()
    
    selected_date_str = request.GET.get('date')
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    if selected_date not in available_dates and available_dates:
        selected_date = available_dates[0]
        
    if selected_date:
        final_theaters = all_theaters.filter(time__date=selected_date)
    else:
        final_theaters = all_theaters

    grouped_theaters = {}
    for t in final_theaters.order_by('name', 'time'):
        if t.name not in grouped_theaters:
            grouped_theaters[t.name] = []
        grouped_theaters[t.name].append(t)
        
    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.update_or_create(
                movie=movie, user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
        return redirect(f"{request.path}?date={selected_date.strftime('%Y-%m-%d') if selected_date else ''}")
        
    reviews = movie.reviews.all().order_by('-created_at')
    
    context = {
        'movie': movie,
        'available_dates': available_dates,
        'selected_date': selected_date,
        'grouped_theaters': grouped_theaters,
        'reviews': reviews,
        'current_city': selected_city,
        'available_cities': available_cities
    }
    return render(request, 'movies/theater_list.html', context)


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theaters = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theaters)
    
    # Check if seats are currently in a 2-minute lock window by someone else
    now = timezone.now()
    for seat in seats:
        if seat.is_locked and seat.locked_until and seat.locked_until > now and seat.locked_by != request.user:
            seat.is_currently_locked = True
        else:
            seat.is_currently_locked = False
    
    if request.method == 'POST':
        selected_seats_ids = request.POST.getlist('seats')
        error_seats = []
        
        if not selected_seats_ids:
            messages.error(request, "No seat selected.")
            return redirect('book_seats', theater_id=theater_id)
        
        now = timezone.now()
        lock_time = now + datetime.timedelta(minutes=2)
        seat_ids = []
        
        try:
            with transaction.atomic():
                # 1. DB Lock: Prevent concurrent DB writes for these specific seats
                try:
                    # Force evaluation by wrapping in list() so SQLite raises the lock exception immediately
                    selected_seats = list(Seat.objects.select_for_update(nowait=True).filter(id__in=selected_seats_ids, theater=theaters))
                except Exception as e:
                    # Database is currently locking these rows (someone is booking them exactly right now)
                    messages.error(request, "Seats are currently being booked by someone else. Try again.")
                    return redirect('book_seats', theater_id=theater_id)
                
                if len(selected_seats) != len(selected_seats_ids):
                    messages.error(request, "Invalid seats selected.")
                    return redirect('book_seats', theater_id=theater_id)
                
                # 2. Redis & DB Verification
                for seat in selected_seats:
                    if seat.is_booked:
                        error_seats.append(seat.seat_number)
                        continue
                    
                    # Check DB lock
                    if seat.is_locked and seat.locked_until and seat.locked_until > now and seat.locked_by != request.user:
                        error_seats.append(seat.seat_number)
                        continue
                    
                    # Try Redis lock (SET NX EX)
                    redis_key = f"seat_lock_{seat.id}"
                    try:
                        # add() works like SET NX, it only sets if key does not exist.
                        is_redis_locked = cache.add(redis_key, request.user.id, timeout=120)
                        if not is_redis_locked:
                            error_seats.append(seat.seat_number)
                    except Exception as e:
                        # Redis crash fallback to DB locking
                        logger.error(f"Redis cache error: {e}. Falling back to DB locking.")
                
                if error_seats:
                    error_message = f"The following seats are unavailable: {', '.join(error_seats)}"
                    messages.error(request, error_message)
                    return redirect('book_seats', theater_id=theater_id)
                
                # 3. Apply locks and Broadcast over WebSockets
                channel_layer = get_channel_layer()
                for seat in selected_seats:
                    seat.is_locked = True
                    seat.locked_by = request.user
                    seat.locked_until = lock_time
                    seat.save()
                    seat_ids.append(seat.id)
                    try:
                        async_to_sync(channel_layer.group_send)(
                            f'theater_{theater_id}',
                            {'type': 'seat_update', 'action': 'locked', 'seat_id': seat.id}
                        )
                    except Exception as e:
                        pass
        except OperationalError:
            # Catch SQLite "database is locked" errors globally for this transaction
            messages.error(request, "Seats are currently being booked by someone else. Try again.")
            return redirect('book_seats', theater_id=theater_id)
            
        # 4. Trigger Celery Task to auto-unlock if payment fails
        try:
            from .tasks import unlock_seats
            unlock_seats.apply_async((seat_ids,), countdown=120)
        except Exception as e:
            logger.error(f"Celery task error: {e}")
            # We can still proceed because we check `locked_until > now` in queries!
        
        # Save to session for the payment flow
        request.session['pending_booking'] = {
            'theater_id': theater_id,
            'seat_ids': seat_ids,
            'lock_expiry': lock_time.isoformat()
        }
        return redirect('payment_view')

    return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats})


@login_required(login_url='/login/')
def payment_view(request):
    pending = request.session.get('pending_booking')
    if not pending:
        return redirect('movie_list')
        
    theater_id = pending['theater_id']
    seat_ids = pending['seat_ids']
    lock_expiry_str = pending['lock_expiry']
    lock_expiry = datetime.datetime.fromisoformat(lock_expiry_str)
    
    from .models import Theater, Seat, FoodItem, Booking, BookingFoodItem
    now = timezone.now()
    if now > lock_expiry:
        del request.session['pending_booking']
        return render(request, 'movies/payment.html', {'error': 'Session expired. Seats have been released.'})
        
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(id__in=seat_ids)
    
    food_items = FoodItem.objects.all()
    
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        idempotency_key = str(uuid.uuid4())
        
        # Calculate food total and build food dict
        food_dict = {}
        food_total = 0

        for key, value in request.POST.items():
            if key.startswith('food_') and int(value) > 0:
                food_id = int(key.split('_')[1])
                quantity = int(value)
                try:
                    food_item = FoodItem.objects.get(id=food_id)
                    food_dict[str(food_id)] = quantity
                    food_total += float(food_item.price) * quantity
                except FoodItem.DoesNotExist:
                    pass
                    
        # Coupon Logic
        coupon_code = request.POST.get('coupon', '').strip().upper()
        ticket_count = len(seats)
        ticket_total = 150.00 * ticket_count
        subtotal = ticket_total + food_total
        discount = 0
        
        if coupon_code == 'TAP100' and ticket_count >= 2:
            discount = 100
        elif coupon_code == 'PAYTM150':
            discount = 150
        elif coupon_code == 'SUPER10':
            discount = subtotal * 0.10
        elif coupon_code == 'FIRST20':
            discount = subtotal * 0.20
            if discount > 150: discount = 150
        elif coupon_code == 'BOGO' and ticket_count >= 2:
            discount = 150
            
        total_amount = subtotal - discount
        if total_amount < 0: total_amount = 0
        
        # We consolidate everything into a single line item because Stripe doesn't allow negative line items easily.
        line_items = [{
            'price_data': {
                'currency': 'inr',
                'unit_amount': int(total_amount * 100),
                'product_data': {
                    'name': f'Tickets & Food for {theater.movie.name} ({theater.name})' + (f' - Coupon {coupon_code}' if discount > 0 else ''),
                },
            },
            'quantity': 1,
        }]
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=settings.DOMAIN_URL + reverse('payment_success') + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.DOMAIN_URL + reverse('payment_cancel'),
                client_reference_id=str(request.user.id),
                metadata={
                    'theater_id': theater.id,
                },
                idempotency_key=idempotency_key
            )
            
            # Save pending payment to DB (seat_ids now contains both seats and food)
            Payment.objects.create(
                user=request.user,
                stripe_checkout_id=checkout_session.id,
                amount=total_amount,
                theater=theater,
                seat_ids={"seats": seat_ids, "food": food_dict},
                status='PENDING'
            )
            
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            logger.error(f"Stripe error: {e}")
            messages.error(request, "Payment gateway error. Try again.")
            return redirect('payment_view')

    time_left = (lock_expiry - now).total_seconds()
    return render(request, 'movies/payment.html', {
        'theater': theater, 
        'seats': seats, 
        'total': len(seats) * 150,
        'time_left': int(time_left),
        'food_items': food_items
    })

@login_required(login_url='/login/')
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
            
    return render(request, 'movies/payment_success.html')

@login_required(login_url='/login/')
def payment_cancel(request):
    return render(request, 'movies/payment_cancel.html')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        with open("webhook_debug.txt", "a") as f: f.write(f"ValueError: {e}\n")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        with open("webhook_debug.txt", "a") as f: f.write(f"SigError: {e}\n")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        with open("webhook_debug.txt", "a") as f:
            f.write(f"Webhook hit for session {session['id']}\n")
            
        try:
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
                return HttpResponse(status=400)
            with open("webhook_debug.txt", "a") as f:
                f.write(f"Payment not found for {session['id']}\n")
            return HttpResponse(status=400)
            
        # Idempotency check: Ignore duplicate webhooks if already SUCCESS
        if payment.status == 'SUCCESS':
            return HttpResponse(status=200)
            
        with transaction.atomic():
            payment.status = 'SUCCESS'
            payment.save()
            
            booking_data = payment.seat_ids
            if isinstance(booking_data, dict) and "seats" in booking_data:
                actual_seat_ids = booking_data["seats"]
                food_dict = booking_data.get("food", {})
            else:
                actual_seat_ids = booking_data
                food_dict = {}
                
            seats = Seat.objects.select_for_update().filter(id__in=actual_seat_ids, is_booked=False)
            booking_ids = []
            
            from .models import BookingFoodItem, FoodItem
            
            for seat in seats:
                try:
                    booking = Booking.objects.create(
                        user=payment.user,
                        seat=seat,
                        movie=payment.theater.movie,
                        theater=payment.theater
                    )
                    booking_ids.append(booking.id)
                    
                    # Add food items to this booking
                    for food_id, quantity in food_dict.items():
                        food_item = FoodItem.objects.get(id=int(food_id))
                        BookingFoodItem.objects.create(
                            booking=booking, 
                            food_item=food_item, 
                            quantity=quantity
                        )
                        
                    seat.is_booked = True
                    seat.is_locked = False
                    seat.locked_by = None
                    seat.locked_until = None
                    seat.save()
                    
                    # Broadcast booking over WebSockets
                    channel_layer = get_channel_layer()
                    try:
                        async_to_sync(channel_layer.group_send)(
                            f'theater_{payment.theater.id}',
                            {'type': 'seat_update', 'action': 'booked', 'seat_id': seat.id}
                        )
                    except Exception as e:
                        pass
                    
                    redis_key = f"seat_lock_{seat.id}"
                    try:
                        cache.delete(redis_key)
                    except Exception as e:
                        logger.error(f"Redis cache error on delete: {e}")
                except IntegrityError:
                    pass
                    
            if booking_ids:
                transaction.on_commit(lambda: send_ticket_email.delay(booking_ids, session['id']))

    return HttpResponse(status=200)


@login_required(login_url='/login/')

@login_required(login_url='/login/')
def download_event_ticket_pdf(request, booking_id):
    booking = get_object_or_404(EventBooking, id=booking_id, user=request.user)
    template_path = 'users/event_ticket_pdf.html'
    context = {'booking': booking}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="event_ticket_{booking.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_ticket_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    template_path = 'users/ticket_pdf.html'
    context = {'booking': booking}
    
    response = HttpResponse(content_type='application/pdf')
    # Use inline styling for filename download
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def admin_dashboard(request):
    # Check cache first for optimization
    cache_key = 'admin_dashboard_metrics'
    try:
        context = cache.get(cache_key)
    except Exception:
        context = None
    
    if not context:
        now = timezone.now()
        
        # Optimize Revenue Calculation (Database Aggregation)
        def get_revenue(days_back=None):
            q = Q(status='SUCCESS')
            if days_back is not None:
                q &= Q(created_at__gte=now - datetime.timedelta(days=days_back))
            agg = Payment.objects.filter(q).aggregate(total=Sum('amount'))
            return float(agg['total'] or 0)
            
        # Most popular movies (Group By Movie, Count Bookings)
        popular_movies = list(Movie.objects.annotate(
            booking_count=Count('booking')
        ).order_by('-booking_count')[:5].values('name', 'booking_count'))
        
        # Busiest theaters (Occupancy Rate)
        busiest_theaters = list(Theater.objects.annotate(
            total_seats=Count('seats'),
            booked_seats=Count('seats', filter=Q(seats__is_booked=True))
        ).annotate(
            occupancy=ExpressionWrapper(
                F('booked_seats') * 100.0 / F('total_seats'),
                output_field=FloatField()
            )
        ).order_by('-occupancy')[:5].values('name', 'occupancy', 'movie__name'))
        
        # Peak booking hours (Extract Hour from DateTime)
        peak_hours_query = Booking.objects.annotate(
            hour=ExtractHour('booked_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        peak_hours_data = {item['hour']: item['count'] for item in peak_hours_query if item['hour'] is not None}
        peak_hours = [{'hour': h, 'count': peak_hours_data.get(h, 0)} for h in range(24)]
        
        # Cancellation rates
        total_payments = Payment.objects.count()
        failed_payments = Payment.objects.filter(status='FAILED').count()
        cancellation_rate = (failed_payments / total_payments * 100) if total_payments > 0 else 0
        
        context = {
            'revenue': {
                'daily': get_revenue(1),
                'weekly': get_revenue(7),
                'monthly': get_revenue(30),
                'total': get_revenue(None)
            },
            'popular_movies': popular_movies,
            'busiest_theaters': busiest_theaters,
            'peak_hours': peak_hours,
            'cancellation_rate': round(cancellation_rate, 2),
            'total_bookings': Booking.objects.count()
        }
        
        # Cache for 30 seconds for near real-time updates
        try:
            cache.set(cache_key, context, 30)
        except Exception:
            pass
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
        
    return render(request, 'movies/admin_dashboard.html', context)


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


def event_category(request, category):
    # Mapping for Workshop -> Theatre Plays
    if category == 'Workshop':
        events = Event.objects.filter(category__in=['Workshop', 'Theatre'])
    else:
        events = Event.objects.filter(category__iexact=category)
    return render(request, 'movies/event_list.html', {'events': events, 'category': category})

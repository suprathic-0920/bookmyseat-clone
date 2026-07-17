try:
    from celery import shared_task
except ImportError:
    # Fallback for Vercel where celery is not installed
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
from django.utils import timezone
from .models import Seat, Booking, EmailLog
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def unlock_seats(seat_ids):
    """
    Unlock seats if they haven't been booked (paid for) after the 2-minute window.
    """
    now = timezone.now()
    seats = Seat.objects.filter(id__in=seat_ids, is_booked=False, is_locked=True)
    
    unlocked_count = 0
    for seat in seats:
        if seat.locked_until and seat.locked_until <= now:
            seat.is_locked = False
            seat.locked_by = None
            seat.locked_until = None
            seat.save()
            unlocked_count += 1
            
    return f"Unlocked {unlocked_count} seats."

@shared_task(bind=True, max_retries=3)
def send_ticket_email(self, booking_ids, payment_id):
    """
    Background task to send a confirmation email after booking.
    Retries up to 3 times on failure.
    """
    try:
        bookings = Booking.objects.filter(id__in=booking_ids)
        if not bookings.exists():
            logger.warning(f"No bookings found for ids {booking_ids}")
            return "No bookings found."
            
        first_booking = bookings.first()
        user = first_booking.user
        movie = first_booking.movie
        theater = first_booking.theater
        
        seat_numbers = [b.seat.seat_number for b in bookings]
        
        # Prepare context for the email template
        context = {
            'user': user,
            'movie': movie,
            'theater': theater,
            'seat_numbers': ', '.join(seat_numbers),
            'payment_id': payment_id,
            'domain': settings.DOMAIN_URL
        }
        
        # Render HTML and plain-text templates
        html_content = render_to_string('movies/emails/ticket_email.html', context)
        text_content = render_to_string('movies/emails/ticket_email.txt', context)
        
        subject = f"Your Tickets for {movie.name} are Confirmed!"
        from_email = getattr(settings, 'EMAIL_HOST_USER', 'no-reply@bookmyseat.com')
        if not from_email:
            from_email = 'no-reply@bookmyseat.com'
            
        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        msg.send()
        
        # Log success
        EmailLog.objects.create(
            user=user,
            subject=subject,
            status='SUCCESS'
        )
        
        logger.info(f"Successfully sent confirmation email to {user.email} for payment {payment_id}")
        return f"Email sent to {user.email}"
        
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        
        # Determine the user object to log if it exists
        user_to_log = None
        subject_to_log = "Ticket Booking Email"
        try:
            bookings = Booking.objects.filter(id__in=booking_ids)
            if bookings.exists():
                user_to_log = bookings.first().user
                subject_to_log = f"Your Tickets for {bookings.first().movie.name} are Confirmed!"
        except:
            pass

        if user_to_log:
            EmailLog.objects.create(
                user=user_to_log,
                subject=subject_to_log,
                status='FAILED',
                error_message=str(exc)
            )

        # Implement Retry Logic
        raise self.retry(exc=exc, countdown=60) # Retry after 60 seconds

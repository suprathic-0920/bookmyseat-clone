from django.db import models
from django.contrib.auth.models import User
import datetime 
from django.core.exceptions import ValidationError
import re

# Security validator to prevent XSS and ensure only YouTube links are added
def validate_youtube_url(value):
    youtube_regex = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$'
    if not re.match(youtube_regex, value):
        raise ValidationError('Security Alert: Only valid YouTube URLs are allowed. Please prevent malicious script injections.')

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1, db_index=True)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True) # optional
    genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
    languages = models.ManyToManyField(Language, blank=True, related_name='movies')
    
    # New field for Internship Task 1: Secure YouTube Trailer Embedding
    trailer_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        validators=[validate_youtube_url],
        help_text="Paste the YouTube trailer link here."
    )

    def __str__(self):
        return self.name

class Theater(models.Model):
    SCREEN_TYPE_CHOICES = [
        ('2D', '2D'),
        ('3D', '3D'),
        ('IMAX', 'IMAX'),
        ('4K DOLBY ATMOS', '4K Dolby Atmos'),
        ('LASER DTS X', 'Laser DTS X'),
        ('LASER ATMOS', 'Laser Atmos'),
        ('4K ATMOS', '4K Atmos'),
        ('DOLBY 7.1', 'Dolby 7.1'),
    ]
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()
    city = models.CharField(max_length=100, default='Chennai')
    screen_type = models.CharField(max_length=50, choices=SCREEN_TYPE_CHOICES, default='2D')

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    
    # Task 2: Concurrency-Safe Locking
    is_locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.movie.name} - {self.seat.seat_number}'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    seat_ids = models.JSONField(help_text="Stores the IDs of the seats being booked")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - ₹{self.amount} at {self.theater.name}"

class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="food/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class BookingFoodItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='food_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name} for Booking {self.booking.id}"

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return f"{self.user.username}'s review for {self.movie.name} ({self.rating}/5)"

class EmailLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email to {self.user.email} - {self.status} at {self.sent_at}"

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Music', 'Music Concert'),
        ('Comedy', 'Standup Comedy'),
        ('Sports', 'Live Sports'),
        ('Workshop', 'Workshop'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Music')
    venue = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.PositiveIntegerField(default=100)
    available_tickets = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.name} - {self.venue}"

class EventBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    tickets_count = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_time = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.tickets_count}x {self.event.name}"
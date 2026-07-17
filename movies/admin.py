from django.contrib import admin
from .models import Movie, Theater, Seat, Booking, Genre, Language, FoodItem, BookingFoodItem, Review, EmailLog, Event, EventBooking

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'cast','description']

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie','theater','booked_at']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

@admin.register(BookingFoodItem)
class BookingFoodItemAdmin(admin.ModelAdmin):
    list_display = ['booking', 'food_item', 'quantity']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'rating', 'created_at']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'sent_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'venue', 'date_time', 'ticket_price', 'available_tickets']
    list_filter = ['category', 'date_time']
    search_fields = ['name', 'venue']

@admin.register(EventBooking)
class EventBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'tickets_count', 'total_amount', 'booking_time', 'payment_status']
    list_filter = ['payment_status', 'booking_time']
    search_fields = ['user__username', 'event__name', 'stripe_checkout_id']

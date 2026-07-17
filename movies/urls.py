from django.urls import path
from . import views
urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('set-city/', views.set_city, name='set_city'),
    path('detect-city/', views.detect_city_api, name='detect_city_api'),
    path('get-cities/', views.get_cities_api, name='get_cities_api'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    path('payment/', views.payment_view, name='payment_view'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('booking/<int:booking_id>/ticket/', views.download_ticket_pdf, name='download_ticket'),
    path('event/booking/<int:booking_id>/ticket/', views.download_event_ticket_pdf, name='download_event_ticket'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/book/', views.book_event, name='book_event'),
    path('event/payment/success/', views.event_payment_success, name='event_payment_success'),
    path('events/category/<str:category>/', views.event_category, name='event_category'),
]
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/theater/<int:theater_id>/seats/', consumers.SeatSyncConsumer.as_asgi()),
]

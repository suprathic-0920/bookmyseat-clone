import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.models import FoodItem

food_data = [
    {"name": "Large Popcorn (Salted)", "price": 250.00},
    {"name": "Caramel Popcorn", "price": 300.00},
    {"name": "Coca Cola (500ml)", "price": 150.00},
    {"name": "Nachos with Cheese", "price": 200.00},
    {"name": "Hot Dog", "price": 180.00},
    {"name": "Mineral Water", "price": 50.00},
]

print("Seeding Food Items...")
for data in food_data:
    FoodItem.objects.get_or_create(name=data["name"], defaults={"price": data["price"]})
    
print("Food Items seeded successfully!")

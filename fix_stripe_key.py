import os

views_path = os.path.join('movies', 'views.py')
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure we import settings if not already
if "from django.conf import settings" not in content:
    content = "from django.conf import settings\n" + content

# Add stripe.api_key = settings.STRIPE_SECRET_KEY right after import stripe
if "stripe.api_key = settings.STRIPE_SECRET_KEY" not in content:
    content = content.replace("import stripe", "import stripe\nstripe.api_key = settings.STRIPE_SECRET_KEY")

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Stripe API key globally set in views.py")

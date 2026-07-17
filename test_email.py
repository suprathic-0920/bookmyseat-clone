import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

try:
    send_mail(
        'Test Subject',
        'Test Message from Django',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER], # Send to self
        fail_silently=False,
    )
    print("SUCCESS: Email sent without errors!")
except Exception as e:
    print(f"ERROR: {e}")

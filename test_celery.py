import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')
django.setup()

from movies.tasks import send_ticket_email

print("Testing send_ticket_email synchronously...")
try:
    # Use the latest booking ID (e.g. 9)
    result = send_ticket_email([9], 'cs_test_a1vLTLTzoNzg86hKhbKYqKFsHrm4gEvqzafYwfCdxB3cRfNmLTeqQ4quHA')
    print("RESULT:", result)
except Exception as e:
    print("ERROR:", e)

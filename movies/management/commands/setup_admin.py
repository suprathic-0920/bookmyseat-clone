from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a secure admin superuser for the dashboard'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123!')
            self.stdout.write(self.style.SUCCESS('Successfully created admin user with password: AdminPass123!'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))

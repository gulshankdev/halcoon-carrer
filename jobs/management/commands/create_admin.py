from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates a default superuser for HALCON CAREER administration if not already existing."

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Superuser username')
        parser.add_argument('--email', default='admin@halconcareer.com', help='Superuser email')
        parser.add_argument('--password', default='Admin@Halcon2026', help='Superuser password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists."))
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' successfully created with provided credentials."))


from getpass import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a superuser without storing a default password in source code."

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Superuser username')
        parser.add_argument('--email', default='admin@halconcareer.com', help='Superuser email')
        parser.add_argument(
            '--password',
            help='Superuser password (omit to enter it securely at the prompt)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists."))
            return

        if password is None:
            password = getpass('Password: ')
            confirmation = getpass('Password (again): ')
            if password != confirmation:
                raise CommandError('The two passwords did not match.')

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' successfully created."))

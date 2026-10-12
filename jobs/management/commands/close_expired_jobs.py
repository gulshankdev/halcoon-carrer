from django.core.management.base import BaseCommand

from jobs.models import Job


class Command(BaseCommand):
    help = 'Mark published jobs past their application deadline as closed.'

    def handle(self, *args, **options):
        expired_jobs = Job.objects.expired()
        count = expired_jobs.count()
        expired_jobs.update(status=Job.Status.CLOSED, is_published=False)
        self.stdout.write(self.style.SUCCESS(f'Closed {count} expired job(s).'))

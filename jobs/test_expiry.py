from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import Job


class CloseExpiredJobsCommandTests(TestCase):
    def create_job(self, title, **kwargs):
        defaults = {
            'title': title,
            'location': 'Mohali',
            'description': 'Job description.',
            'responsibilities': 'Job responsibilities.',
            'required_skills': 'Python',
            'qualifications': 'Relevant experience.',
            'status': Job.Status.PUBLISHED,
        }
        defaults.update(kwargs)
        return Job.objects.create(**defaults)

    def test_command_closes_only_published_jobs_past_deadline(self):
        expired = self.create_job(
            'Expired',
            application_deadline=timezone.localdate() - timedelta(days=1),
        )
        active = self.create_job(
            'Active',
            application_deadline=timezone.localdate(),
        )
        draft = self.create_job(
            'Draft',
            status=Job.Status.DRAFT,
            application_deadline=timezone.localdate() - timedelta(days=1),
        )

        output = StringIO()
        call_command('close_expired_jobs', stdout=output)

        expired.refresh_from_db()
        active.refresh_from_db()
        draft.refresh_from_db()
        self.assertEqual(expired.status, Job.Status.CLOSED)
        self.assertFalse(expired.is_published)
        self.assertEqual(active.status, Job.Status.PUBLISHED)
        self.assertEqual(draft.status, Job.Status.DRAFT)
        self.assertIn('Closed 1 expired job(s).', output.getvalue())

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Job


class PublicJobsAPITests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Technology')
        self.job = Job.objects.create(
            title='Django API Engineer',
            category=self.category,
            location='Mohali',
            employment_type='Full-time',
            experience_requirements='1-3 Years',
            min_salary=50000,
            max_salary=80000,
            description='Build Django services.',
            responsibilities='Develop and maintain APIs.',
            required_skills='Python, Django, SQL',
            qualifications='Relevant experience.',
            status=Job.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.list_url = reverse('job_api:list')

    def test_job_api_lists_public_jobs_anonymously(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['slug'], self.job.slug)
        self.assertEqual(response.json()['results'][0]['category']['slug'], self.category.slug)

    def test_job_api_hides_drafts_expired_and_inactive_category_jobs(self):
        Job.objects.create(
            title='Private Draft',
            location='Mohali',
            description='Draft only.',
            responsibilities='Private.',
            required_skills='Python',
            qualifications='Relevant experience.',
        )
        Job.objects.create(
            title='Expired Job',
            location='Mohali',
            description='Expired.',
            responsibilities='Expired.',
            required_skills='Python',
            qualifications='Relevant experience.',
            status=Job.Status.PUBLISHED,
            application_deadline=timezone.localdate() - timedelta(days=1),
        )
        inactive_category = Category.objects.create(name='Inactive', active=False)
        Job.objects.create(
            title='Inactive Category Job',
            category=inactive_category,
            location='Mohali',
            description='Not publicly listed.',
            responsibilities='Not publicly listed.',
            required_skills='Python',
            qualifications='Relevant experience.',
            status=Job.Status.PUBLISHED,
        )

        response = self.client.get(self.list_url)
        result_slugs = [result['slug'] for result in response.json()['results']]
        self.assertEqual(result_slugs, [self.job.slug])

    def test_job_api_detail_returns_404_for_non_public_job(self):
        draft = Job.objects.create(
            title='Private Draft',
            location='Mohali',
            description='Draft only.',
            responsibilities='Private.',
            required_skills='Python',
            qualifications='Relevant experience.',
        )
        response = self.client.get(reverse('job_api:detail', args=[draft.slug]))
        self.assertEqual(response.status_code, 404)

    def test_job_api_filters_keyword_and_salary(self):
        response = self.client.get(
            self.list_url,
            {'q': 'Django', 'min_salary': '60000', 'category': self.category.slug},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_job_api_rejects_invalid_salary_filter_and_disallows_writes(self):
        invalid_filter = self.client.get(self.list_url, {'min_salary': '-1'})
        self.assertEqual(invalid_filter.status_code, 400)
        create_attempt = self.client.post(self.list_url, {'title': 'Unauthorized'})
        self.assertEqual(create_attempt.status_code, 405)

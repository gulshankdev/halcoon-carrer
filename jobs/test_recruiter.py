from datetime import timedelta
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import Permission, User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Job


class RecruiterDashboardTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name='Software')
        self.recruiter = User.objects.create_user(
            username='recruiter',
            password='A-strong-password-123',
        )
        permission = Permission.objects.get(codename='manage_recruiter_dashboard')
        self.recruiter.user_permissions.add(permission)

    def job_data(self, **overrides):
        data = {
            'title': 'Django Engineer',
            'company_name': 'Halcon Test Company',
            'category': str(self.category.pk),
            'description': 'Build robust web applications.',
            'responsibilities': 'Design and maintain Django services.',
            'required_skills': 'Python, Django, SQL',
            'min_salary': '50000',
            'max_salary': '80000',
            'salary_period': 'monthly',
            'location': 'Mohali',
            'work_mode': 'Hybrid',
            'employment_type': 'Full-time',
            'experience_requirements': '1-3 Years',
            'min_experience_years': '1',
            'max_experience_years': '3',
            'qualifications': 'Bachelor degree or equivalent experience.',
            'vacancies_count': '2',
            'application_method': 'website',
            'status': Job.Status.DRAFT,
        }
        data.update(overrides)
        return data

    def create_job(self, **overrides):
        data = self.job_data(**overrides)
        data.pop('company_name')
        data['category'] = self.category
        return Job.objects.create(**data)

    def test_anonymous_user_is_redirected_from_dashboard(self):
        response = self.client.get(reverse('recruiter:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('recruiter:login'), response['Location'])

    def test_candidate_without_permission_cannot_open_dashboard(self):
        candidate = User.objects.create_user(
            username='candidate',
            password='Candidate-password-123',
        )
        self.client.force_login(candidate)
        response = self.client.get(reverse('recruiter:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('recruiter:login'), response['Location'])

    def test_recruiter_management_pages_render(self):
        self.client.force_login(self.recruiter)
        pages = [
            'recruiter:dashboard',
            'recruiter:jobs',
            'recruiter:job_add',
            'recruiter:applications',
            'recruiter:categories',
            'recruiter:category_add',
            'recruiter:companies',
            'recruiter:company_add',
            'recruiter:enquiries',
        ]
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(reverse(page)).status_code, 200)

    def test_recruiter_can_create_and_publish_a_job(self):
        self.client.force_login(self.recruiter)
        response = self.client.post(reverse('recruiter:job_add'), self.job_data())
        self.assertRedirects(response, reverse('recruiter:jobs'))
        job = Job.objects.get(title='Django Engineer')
        self.assertEqual(job.status, Job.Status.DRAFT)
        self.assertEqual(job.company.name, 'Halcon Test Company')

        publish_url = reverse(
            'recruiter:job_status',
            kwargs={'pk': job.pk, 'status': Job.Status.PUBLISHED},
        )
        self.client.post(publish_url)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.PUBLISHED)
        self.assertTrue(job.is_published)
        self.assertContains(self.client.get(reverse('jobs:job_list')), 'Django Engineer')
        self.assertContains(self.client.get(reverse('core:home')), 'Django Engineer')

    def test_recruiter_can_upload_job_image(self):
        self.client.force_login(self.recruiter)
        buffer = BytesIO()
        Image.new('RGB', (1, 1), color='white').save(buffer, format='JPEG')
        image = SimpleUploadedFile('job-image.jpg', buffer.getvalue(), content_type='image/jpeg')
        response = self.client.post(
            reverse('recruiter:job_add'),
            {**self.job_data(), 'image': image},
        )
        self.assertRedirects(response, reverse('recruiter:jobs'))
        job = Job.objects.get(title='Django Engineer')
        self.assertTrue(job.image.name.startswith('public_uploads/jobs/'))

    def test_job_form_rejects_invalid_salary_range(self):
        self.client.force_login(self.recruiter)
        response = self.client.post(
            reverse('recruiter:job_add'),
            self.job_data(min_salary='90000', max_salary='80000'),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maximum salary must be greater than or equal to minimum salary.')
        self.assertFalse(Job.objects.exists())

    def test_public_filters_combine_and_expired_jobs_are_hidden(self):
        public_job = self.create_job(
            status=Job.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        expired_job = self.create_job(
            title='Expired Engineer',
            status=Job.Status.PUBLISHED,
            application_deadline=timezone.localdate() - timedelta(days=1),
            published_at=timezone.now() - timedelta(days=10),
        )
        response = self.client.get(
            reverse('jobs:job_list'),
            {'category': self.category.slug, 'work_mode': 'Hybrid', 'min_salary': '60000'},
        )
        self.assertContains(response, public_job.title)
        self.assertNotContains(response, expired_job.title)
        self.assertEqual(
            self.client.get(reverse('jobs:category_jobs', args=[self.category.slug])).status_code,
            200,
        )

    def test_future_published_job_is_not_public_until_publish_date(self):
        scheduled = self.create_job(
            status=Job.Status.PUBLISHED,
            published_at=timezone.now() + timedelta(days=2),
        )
        self.assertNotContains(self.client.get(reverse('jobs:job_list')), scheduled.title)
        self.assertEqual(
            self.client.get(reverse('jobs:job_detail', args=[scheduled.slug])).status_code,
            404,
        )

    def test_expired_job_cannot_accept_candidate_application(self):
        expired = self.create_job(
            status=Job.Status.PUBLISHED,
            application_deadline=timezone.localdate() - timedelta(days=1),
        )
        candidate = User.objects.create_user(
            username='expired-candidate',
            password='Candidate-password-123',
        )
        self.client.force_login(candidate)
        response = self.client.get(reverse('applications:apply', args=[expired.slug]))
        self.assertEqual(response.status_code, 404)

    def test_failed_login_is_rate_limited(self):
        for _ in range(5):
            self.client.post(reverse('recruiter:login'), {'username': 'recruiter', 'password': 'wrong'})
        response = self.client.post(
            reverse('recruiter:login'),
            {'username': 'recruiter', 'password': 'A-strong-password-123'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Too many unsuccessful attempts')

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from jobs.models import Category, Job


class JobsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username="recruiter_staff",
            password="StaffPassword123!",
            is_staff=True
        )

        self.cat_it = Category.objects.create(name="IT & Tech", slug="it-tech")
        self.cat_sales = Category.objects.create(name="Sales", slug="sales")

        self.published_job = Job.objects.create(
            title="Senior Python Architect",
            slug="senior-python-architect",
            category=self.cat_it,
            location="Mohali",
            employment_type="Full-time",
            experience_requirements="5-8 Years",
            min_salary=800000,
            max_salary=1200000,
            description="Leading backend development",
            responsibilities="Architecting code",
            required_skills="Python, Django, Microservices",
            qualifications="B.Tech",
            is_published=True
        )

        self.draft_job = Job.objects.create(
            title="Unpublished Internal Position",
            slug="unpublished-internal-position",
            category=self.cat_it,
            location="Chandigarh",
            employment_type="Full-time",
            experience_requirements="1-3 Years",
            description="Draft JD",
            responsibilities="Internal tasks",
            required_skills="General",
            qualifications="Degree",
            is_published=False  # Unpublished
        )

        self.sales_job = Job.objects.create(
            title="Corporate Account Executive",
            slug="corporate-account-executive",
            category=self.cat_sales,
            location="Delhi NCR",
            employment_type="Full-time",
            experience_requirements="1-3 Years",
            description="Corporate sales role",
            responsibilities="Client meetings",
            required_skills="Sales, CRM",
            qualifications="BBA",
            is_published=True
        )

    def test_job_list_displays_only_published_jobs(self):
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertContains(response, "Corporate Account Executive")
        self.assertNotContains(response, "Unpublished Internal Position")

    def test_job_search_by_keyword(self):
        response = self.client.get(reverse('jobs:job_list') + '?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertNotContains(response, "Corporate Account Executive")

    def test_job_filter_by_category(self):
        response = self.client.get(reverse('jobs:job_list') + '?category=sales')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Corporate Account Executive")
        self.assertNotContains(response, "Senior Python Architect")

    def test_job_filter_by_location(self):
        response = self.client.get(reverse('jobs:job_list') + '?location=Mohali')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertNotContains(response, "Corporate Account Executive")

    def test_job_detail_view_published(self):
        response = self.client.get(reverse('jobs:job_detail', args=[self.published_job.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Architect")
        self.assertContains(response, "₹800,000 - ₹1,200,000")

    def test_job_detail_unpublished_is_404_for_anonymous(self):
        response = self.client.get(reverse('jobs:job_detail', args=[self.draft_job.slug]))
        self.assertEqual(response.status_code, 404)

    def test_job_detail_unpublished_is_accessible_to_staff(self):
        self.client.login(username='recruiter_staff', password='StaffPassword123!')
        response = self.client.get(reverse('jobs:job_detail', args=[self.draft_job.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unpublished Internal Position")

    def test_salary_display_property(self):
        self.assertEqual(self.published_job.salary_display, "₹800,000 - ₹1,200,000")
        self.published_job.hide_salary = True
        self.assertEqual(self.published_job.salary_display, "Best in Industry")

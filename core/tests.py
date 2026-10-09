from django.test import TestCase, Client
from django.urls import reverse
from core.models import ContactMessage
from jobs.models import Category, Job


class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Technology",
            slug="technology"
        )
        self.job = Job.objects.create(
            title="Software Developer",
            slug="software-developer",
            category=self.category,
            location="Mohali",
            employment_type="Full-time",
            experience_requirements="1-3 Years",
            description="Sample description",
            responsibilities="Sample responsibilities",
            required_skills="Python",
            qualifications="Degree",
            is_published=True,
            is_featured=True
        )

    def test_homepage_loads_successfully(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertContains(response, "Connecting Talent. Creating Opportunities.")
        self.assertContains(response, "Software Developer")
        self.assertContains(response, "Mohali")
        self.assertIn('featured_jobs', response.context)
        self.assertIn('latest_jobs', response.context)

    def test_about_page_loads(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')
        self.assertContains(response, "About Our Consultancy")

    def test_services_page_loads(self):
        response = self.client.get(reverse('core:services'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/services.html')
        self.assertContains(response, "Permanent Staffing")
        self.assertContains(response, "Fresher Recruitment")

    def test_contact_page_get(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "+91 9216033444")
        self.assertContains(response, "SCO 12–13, 2nd Floor, Phase 11, Mohali")

    def test_contact_page_post_valid(self):
        data = {
            'full_name': 'Candidate Inquiry',
            'email': 'inquiry@example.com',
            'phone': '+91 9876543210',
            'subject': 'General Career Inquiry',
            'message': 'Looking for opportunities in Mohali.',
            'website': '',  # Honeypot empty
        }
        response = self.client.post(reverse('core:contact'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email='inquiry@example.com').exists())

    def test_contact_page_post_honeypot_spam_rejected(self):
        data = {
            'full_name': 'Bot Spammer',
            'email': 'bot@spam.com',
            'subject': 'Buy crypto',
            'message': 'Spam message content',
            'website': 'http://spamsite.com',  # Filled honeypot
        }
        response = self.client.post(reverse('core:contact'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactMessage.objects.filter(email='bot@spam.com').exists())

    def test_legal_pages(self):
        privacy_resp = self.client.get(reverse('core:privacy_policy'))
        self.assertEqual(privacy_resp.status_code, 200)
        terms_resp = self.client.get(reverse('core:terms_of_service'))
        self.assertEqual(terms_resp.status_code, 200)
        consent_resp = self.client.get(reverse('core:candidate_consent'))
        self.assertEqual(consent_resp.status_code, 200)

    def test_health_check_endpoint(self):
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'healthy')

    def test_robots_txt(self):
        response = self.client.get(reverse('core:robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('Disallow: /admin/', response.content.decode())

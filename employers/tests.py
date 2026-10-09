from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from employers.models import EmployerEnquiry


class EmployersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username="admin_employer",
            password="AdminPass123!",
            is_staff=True
        )

    def test_employer_enquiry_page_get(self):
        response = self.client.get(reverse('employers:enquiry'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submit Hiring Requirements")
        self.assertContains(response, "Corporate Contact Details")

    def test_employer_enquiry_post_valid(self):
        data = {
            'contact_person': 'Anita Roy',
            'company_name': 'Apex Technologies Pvt Ltd',
            'email': 'hr@apextech.com',
            'phone': '+91 9216033444',
            'hiring_requirements': 'Need 3 Senior Python Engineers in Mohali',
            'vacancies_count': 3,
            'required_skills': 'Python, Django, AWS',
            'message': 'Immediate joining within 30 days.',
            'company_website_url': '',  # Honeypot empty
        }
        response = self.client.post(reverse('employers:enquiry'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('employers:enquiry_success'))

        enquiry = EmployerEnquiry.objects.filter(company_name='Apex Technologies Pvt Ltd').first()
        self.assertIsNotNone(enquiry)
        self.assertEqual(enquiry.contact_person, 'Anita Roy')
        self.assertEqual(enquiry.vacancies_count, 3)
        self.assertEqual(enquiry.status, 'New')

    def test_employer_enquiry_honeypot_spam_rejected(self):
        data = {
            'contact_person': 'Spam Bot',
            'company_name': 'Spam Corp',
            'email': 'bot@spam.com',
            'phone': '+91 9999999999',
            'hiring_requirements': 'Buy followers',
            'vacancies_count': 1,
            'company_website_url': 'http://automatedspam.com',  # Filled honeypot
        }
        response = self.client.post(reverse('employers:enquiry'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(EmployerEnquiry.objects.filter(email='bot@spam.com').exists())

    def test_employer_enquiry_missing_fields_rejected(self):
        data = {
            'contact_person': '',
            'company_name': '',
            'email': 'invalid-email',
            'phone': '',
            'hiring_requirements': '',
            'vacancies_count': 0,
        }
        response = self.client.post(reverse('employers:enquiry'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(EmployerEnquiry.objects.exists())

    def test_employer_success_page(self):
        session = self.client.session
        session['latest_enquiry_company'] = 'Acme Corp'
        session.save()
        response = self.client.get(reverse('employers:enquiry_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acme Corp")

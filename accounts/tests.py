import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from accounts.models import CandidateProfile
from accounts.validators import validate_resume_file


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate_user = User.objects.create_user(
            username="candidate1",
            email="candidate1@example.com",
            password="SecurePassword123!",
            first_name="Rohan",
            last_name="Sharma"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="SecurePassword123!",
            first_name="Priya",
            last_name="Verma"
        )
        self.staff_user = User.objects.create_user(
            username="staffadmin",
            email="staff@example.com",
            password="SecurePassword123!",
            is_staff=True
        )

    def test_candidate_registration_success(self):
        data = {
            'username': 'newapplicant',
            'first_name': 'Aman',
            'last_name': 'Singh',
            'email': 'aman.singh@example.com',
            'phone': '+91 9876543211',
            'password1': 'StrongPass2026@',
            'password2': 'StrongPass2026@',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newapplicant').exists())
        user = User.objects.get(username='newapplicant')
        self.assertEqual(user.candidate_profile.phone, '+91 9876543211')

    def test_registration_password_mismatch(self):
        data = {
            'username': 'mismatchuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'mismatch@example.com',
            'password1': 'PassOne123!',
            'password2': 'PassTwo456!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())

    def test_registration_duplicate_email(self):
        data = {
            'username': 'duplicateemailuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'candidate1@example.com',  # Already exists
            'password1': 'StrongPass2026@',
            'password2': 'StrongPass2026@',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='duplicateemailuser').exists())

    def test_candidate_login_and_logout(self):
        # Login
        login_response = self.client.post(reverse('accounts:login'), {
            'username': 'candidate1',
            'password': 'SecurePassword123!'
        })
        self.assertEqual(login_response.status_code, 302)

        # Profile is accessible when logged in
        profile_response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, "Rohan Sharma")

        # Logout
        logout_response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(logout_response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_update(self):
        self.client.login(username='candidate1', password='SecurePassword123!')
        update_data = {
            'first_name': 'Rohan',
            'last_name': 'Sharma',
            'email': 'rohan.updated@example.com',
            'phone': '+91 9216033444',
            'location': 'Mohali, Punjab',
            'skills': 'Python, Django, PostgreSQL',
            'education': 'B.Tech CSE',
            'experience_summary': '3 years developing web applications',
        }
        response = self.client.post(reverse('accounts:profile'), update_data)
        self.assertEqual(response.status_code, 302)

        self.candidate_user.refresh_from_db()
        self.assertEqual(self.candidate_user.email, 'rohan.updated@example.com')
        self.assertEqual(self.candidate_user.candidate_profile.location, 'Mohali, Punjab')
        self.assertEqual(self.candidate_user.candidate_profile.skills, 'Python, Django, PostgreSQL')

    def test_resume_validator_formats_and_size(self):
        # Valid PDF
        valid_pdf = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        try:
            validate_resume_file(valid_pdf)
        except ValidationError:
            self.fail("validate_resume_file raised ValidationError unexpectedly for valid PDF!")

        # Invalid extension (.exe)
        invalid_exe = SimpleUploadedFile("resume.exe", b"executable content", content_type="application/x-dosexec")
        with self.assertRaises(ValidationError):
            validate_resume_file(invalid_exe)

        # Oversized file (> 5MB)
        large_content = b"x" * (6 * 1024 * 1024)
        oversized_pdf = SimpleUploadedFile("large_resume.pdf", large_content, content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_resume_file(oversized_pdf)

    def test_secure_resume_download_access_control(self):
        profile = self.candidate_user.candidate_profile
        profile.resume = SimpleUploadedFile("rohan_cv.pdf", b"%PDF-1.4 sample resume", content_type="application/pdf")
        profile.save()

        # 1. Unauthenticated request should redirect to login
        unauth_resp = self.client.get(reverse('accounts:download_resume', args=[self.candidate_user.id]))
        self.assertEqual(unauth_resp.status_code, 302)

        # 2. Owner candidate can download (200)
        self.client.login(username='candidate1', password='SecurePassword123!')
        owner_resp = self.client.get(reverse('accounts:download_resume', args=[self.candidate_user.id]))
        self.assertEqual(owner_resp.status_code, 200)
        self.client.logout()

        # 3. Another candidate should be forbidden (403)
        self.client.login(username='otheruser', password='SecurePassword123!')
        other_resp = self.client.get(reverse('accounts:download_resume', args=[self.candidate_user.id]))
        self.assertEqual(other_resp.status_code, 403)
        self.client.logout()

        # 4. Staff administrator can download (200)
        self.client.login(username='staffadmin', password='SecurePassword123!')
        staff_resp = self.client.get(reverse('accounts:download_resume', args=[self.candidate_user.id]))
        self.assertEqual(staff_resp.status_code, 200)

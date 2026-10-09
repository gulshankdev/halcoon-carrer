from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Category, Job
from applications.models import JobApplication


class ApplicationsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate = User.objects.create_user(
            username="candidate_applicant",
            email="applicant@example.com",
            password="ApplicantPass123!",
            first_name="Vikas",
            last_name="Kumar"
        )
        self.other_candidate = User.objects.create_user(
            username="other_applicant",
            email="otherapplicant@example.com",
            password="ApplicantPass123!",
            first_name="Sunil",
            last_name="Gupta"
        )
        self.staff_user = User.objects.create_user(
            username="recruiter",
            password="StaffPass123!",
            is_staff=True
        )

        self.category = Category.objects.create(name="Tech", slug="tech")
        self.job = Job.objects.create(
            title="Backend Python Developer",
            slug="backend-python-developer",
            category=self.category,
            location="Mohali",
            employment_type="Full-time",
            experience_requirements="1-3 Years",
            description="Detailed job role",
            responsibilities="Coding and testing",
            required_skills="Python, Django",
            qualifications="B.Tech",
            is_published=True
        )

    def test_apply_requires_authentication(self):
        response = self.client.get(reverse('applications:apply', args=[self.job.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_apply_submission_success(self):
        self.client.login(username='candidate_applicant', password='ApplicantPass123!')
        resume_file = SimpleUploadedFile("vikas_resume.pdf", b"%PDF-1.4 test resume bytes", content_type="application/pdf")
        data = {
            'full_name': 'Vikas Kumar',
            'email': 'applicant@example.com',
            'phone': '+91 9216033444',
            'cover_letter': 'Excited to apply for this backend vacancy.',
            'resume_file': resume_file,
            'use_existing_resume': False,
        }
        response = self.client.post(reverse('applications:apply', args=[self.job.slug]), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('applications:my_applications'))

        application = JobApplication.objects.filter(candidate=self.candidate, job=self.job).first()
        self.assertIsNotNone(application)
        self.assertEqual(application.status, 'Submitted')
        self.assertEqual(application.full_name, 'Vikas Kumar')

    def test_duplicate_application_prevention(self):
        # Create an existing application
        resume_file = SimpleUploadedFile("first_resume.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            full_name="Vikas Kumar",
            email="applicant@example.com",
            phone="+91 9216033444",
            resume_file=resume_file,
            status="Submitted"
        )

        self.client.login(username='candidate_applicant', password='ApplicantPass123!')

        # Attempt to GET the apply page again
        get_resp = self.client.get(reverse('applications:apply', args=[self.job.slug]))
        self.assertEqual(get_resp.status_code, 302)
        self.assertRedirects(get_resp, reverse('applications:my_applications'))

        # Attempt to POST another application
        second_resume = SimpleUploadedFile("second_resume.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        data = {
            'full_name': 'Vikas Kumar',
            'email': 'applicant@example.com',
            'phone': '+91 9216033444',
            'resume_file': second_resume,
        }
        post_resp = self.client.post(reverse('applications:apply', args=[self.job.slug]), data)
        self.assertEqual(post_resp.status_code, 302)
        self.assertRedirects(post_resp, reverse('applications:my_applications'))

        # DB count must remain strictly 1
        self.assertEqual(JobApplication.objects.filter(candidate=self.candidate, job=self.job).count(), 1)

    def test_my_applications_view(self):
        resume_file = SimpleUploadedFile("test_cv.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            full_name="Vikas Kumar",
            email="applicant@example.com",
            phone="+91 9216033444",
            resume_file=resume_file,
            status="Under Review"
        )
        self.client.login(username='candidate_applicant', password='ApplicantPass123!')
        response = self.client.get(reverse('applications:my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Python Developer")
        self.assertContains(response, "Under Review")

    def test_secure_application_resume_access_control(self):
        resume_file = SimpleUploadedFile("confidential_cv.pdf", b"%PDF-1.4 secure resume data", content_type="application/pdf")
        app = JobApplication.objects.create(
            candidate=self.candidate,
            job=self.job,
            full_name="Vikas Kumar",
            email="applicant@example.com",
            phone="+91 9216033444",
            resume_file=resume_file,
            status="Submitted"
        )

        url = reverse('applications:download_resume', args=[app.id])

        # 1. Unauthenticated gets redirected
        unauth_resp = self.client.get(url)
        self.assertEqual(unauth_resp.status_code, 302)

        # 2. Candidate applicant owner gets 200
        self.client.login(username='candidate_applicant', password='ApplicantPass123!')
        owner_resp = self.client.get(url)
        self.assertEqual(owner_resp.status_code, 200)
        self.client.logout()

        # 3. Different candidate gets 403 Forbidden
        self.client.login(username='other_applicant', password='ApplicantPass123!')
        other_resp = self.client.get(url)
        self.assertEqual(other_resp.status_code, 403)
        self.client.logout()

        # 4. Staff recruiter gets 200
        self.client.login(username='recruiter', password='StaffPass123!')
        staff_resp = self.client.get(url)
        self.assertEqual(staff_resp.status_code, 200)

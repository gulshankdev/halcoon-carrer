from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job
from accounts.validators import validate_resume_file


class JobApplication(models.Model):
    """
    Candidate application submitted for a specific Job vacancy.
    """
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    ]

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume_file = models.FileField(
        upload_to='resumes/applications/%Y/%m/',
        validators=[validate_resume_file],
        help_text="Uploaded resume in PDF or DOCX format (Max 5MB)"
    )
    cover_letter = models.TextField(
        blank=True,
        help_text="Optional cover letter or additional notes for the recruiter"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Submitted'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'job'],
                name='unique_candidate_job_application'
            )
        ]
        indexes = [
            models.Index(fields=['candidate', '-submitted_at']),
            models.Index(fields=['job', 'status']),
        ]

    def __str__(self):
        return f"{self.full_name} applied for {self.job.title} ({self.status})"

    @property
    def status_badge_class(self):
        """Bootstrap badge class for application status."""
        badge_map = {
            'Submitted': 'badge bg-secondary',
            'Under Review': 'badge bg-info text-dark',
            'Shortlisted': 'badge bg-primary',
            'Interview': 'badge bg-warning text-dark',
            'Selected': 'badge bg-success',
            'Rejected': 'badge bg-danger',
        }
        return badge_map.get(self.status, 'badge bg-secondary')

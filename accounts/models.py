from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validate_resume_file


class CandidateProfile(models.Model):
    """
    Profile information for candidates registered on HALCON CAREER.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )
    phone = models.CharField(max_length=20, blank=True, help_text="Contact telephone number")
    location = models.CharField(max_length=150, blank=True, help_text="City, State, or Preferred Location")
    skills = models.TextField(
        blank=True,
        help_text="Key skills (e.g. Python, SQL, Project Management, Sales)"
    )
    education = models.TextField(
        blank=True,
        help_text="Educational background, highest degree, institution"
    )
    experience_summary = models.TextField(
        blank=True,
        help_text="Summary of total work experience, key roles, and domains"
    )
    resume = models.FileField(
        upload_to='resumes/candidate_profiles/',
        blank=True,
        null=True,
        validators=[validate_resume_file],
        help_text="Upload your resume in PDF or DOCX format (Max 5MB)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Candidate Profile"
        verbose_name_plural = "Candidate Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Profile"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_or_update_candidate_profile(sender, instance, created, **kwargs):
    """Ensure a CandidateProfile exists whenever a User is created."""
    if created:
        CandidateProfile.objects.get_or_create(user=instance)


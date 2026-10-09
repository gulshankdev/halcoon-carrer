from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Industry category for job listings."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of this domain or industry")
    icon = models.CharField(
        max_length=50,
        default='bi-briefcase',
        help_text="Bootstrap Icon class name, e.g., 'bi-laptop', 'bi-gear', 'bi-hospital'"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:job_list') + f'?category={self.slug}'


class Job(models.Model):
    """Job vacancy listed by HALCON CAREER."""

    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]

    EXPERIENCE_CHOICES = [
        ('Fresher', 'Fresher (0 - 1 Years)'),
        ('1-3 Years', '1 - 3 Years'),
        ('3-5 Years', '3 - 5 Years'),
        ('5-8 Years', '5 - 8 Years'),
        ('8+ Years', '8+ Years'),
        ('Any Experience', 'Any Experience'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='jobs'
    )
    employer_name = models.CharField(
        max_length=200,
        blank=True,
        default='Confidential Client',
        help_text="Client/Employer name or 'Confidential Client' if undisclosed"
    )
    location = models.CharField(
        max_length=150,
        help_text="e.g. Mohali, Chandigarh, Delhi NCR, Remote"
    )
    employment_type = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='Full-time'
    )
    experience_requirements = models.CharField(
        max_length=100,
        choices=EXPERIENCE_CHOICES,
        default='Any Experience'
    )
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum annual CTC or monthly salary in INR"
    )
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum annual CTC or monthly salary in INR"
    )
    salary_negotiable = models.BooleanField(
        default=False,
        help_text="Check if salary is negotiable"
    )
    hide_salary = models.BooleanField(
        default=False,
        help_text="Check to display 'Best in Industry / Disclosed on Interview'"
    )
    description = models.TextField(
        help_text="Detailed overview of the job role and position"
    )
    responsibilities = models.TextField(
        help_text="Bullet points or detailed breakdown of key duties"
    )
    required_skills = models.TextField(
        help_text="Key skills, tools, and competencies expected"
    )
    qualifications = models.TextField(
        help_text="Education, certifications, or minimum criteria required"
    )
    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Optional last date to receive applications"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this vacancy prominently on the homepage"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Set to False to hold/unpublish this vacancy"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Vacancy"
        verbose_name_plural = "Job Vacancies"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['location']),
            models.Index(fields=['employment_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    @property
    def salary_display(self):
        """Format salary clearly for the UI."""
        if self.hide_salary:
            return "Best in Industry"
        if self.min_salary and self.max_salary:
            return f"₹{int(self.min_salary):,} - ₹{int(self.max_salary):,}"
        elif self.min_salary:
            return f"From ₹{int(self.min_salary):,}"
        elif self.max_salary:
            return f"Up to ₹{int(self.max_salary):,}"
        elif self.salary_negotiable:
            return "Negotiable"
        return "Disclosed on Interview"

    @property
    def is_active_for_application(self):
        if not self.is_published:
            return False
        if self.application_deadline and self.application_deadline < timezone.now().date():
            return False
        return True

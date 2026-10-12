from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from employers.models import Company
from datetime import timedelta


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
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:job_list') + f'?category={self.slug}'


class JobQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Job.Status.PUBLISHED).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
        )

    def open(self):
        today = timezone.localdate()
        return self.published().filter(
            Q(application_deadline__isnull=True) |
            Q(application_deadline__gte=today)
        )

    def expired(self):
        return self.filter(
            status=Job.Status.PUBLISHED,
            application_deadline__lt=timezone.localdate(),
        ).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
        )


class Job(models.Model):
    """Job vacancy listed by HALCON CAREER."""

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        PUBLISHED = 'Published', 'Published'
        CLOSED = 'Closed', 'Closed'

    class WorkMode(models.TextChoices):
        ON_SITE = 'On-site', 'On-site'
        HYBRID = 'Hybrid', 'Hybrid'
        REMOTE = 'Remote', 'Remote'

    class ApplicationMethod(models.TextChoices):
        WEBSITE = 'website', 'HALCON CAREER application form'
        EMAIL = 'email', 'Official email'
        EXTERNAL_URL = 'external_url', 'Verified external application URL'

    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
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
    image = models.ImageField(
        upload_to='public_uploads/jobs/',
        blank=True,
        help_text="Main job image/banner shown on the public job page and card."
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
    salary_period = models.CharField(
        max_length=10,
        choices=[('monthly', 'Per month'), ('yearly', 'Per year')],
        default='yearly',
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
        default=False,
        help_text="Compatibility flag; use Status to manage publication."
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
    )
    work_mode = models.CharField(
        max_length=10,
        choices=WorkMode.choices,
        default=WorkMode.ON_SITE,
    )
    min_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Minimum required experience in years."
    )
    max_experience_years = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Maximum required experience in years."
    )
    vacancies_count = models.PositiveIntegerField(default=1)
    location_country = models.CharField(
        max_length=2,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code, used for verified job metadata."
    )
    application_method = models.CharField(
        max_length=20,
        choices=ApplicationMethod.choices,
        default=ApplicationMethod.WEBSITE,
    )
    application_email = models.EmailField(blank=True)
    application_url = models.URLField(blank=True)
    source = models.CharField(
        max_length=200,
        blank=True,
        help_text="Internal source or verification reference; never shown as an application link."
    )
    source_url = models.URLField(
        blank=True,
        help_text="Source link for recruiter verification; never shown as an application link."
    )
    is_verified = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

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
        permissions = [('manage_recruiter_dashboard', 'Can manage recruiter dashboard')]

    def __str__(self):
        return f"{self.title} - {self.location}"

    def __init__(self, *args, **kwargs):
        legacy_published = kwargs.get('is_published') is True
        status_was_supplied = 'status' in kwargs
        super().__init__(*args, **kwargs)
        if legacy_published and not status_was_supplied:
            self.status = self.Status.PUBLISHED

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        self.is_published = self.status == self.Status.PUBLISHED
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {
                'is_published', 'status', 'published_at'
            }
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        errors = {}
        if self.min_salary is not None and self.min_salary < 0:
            errors['min_salary'] = "Minimum salary cannot be negative."
        if self.max_salary is not None and self.max_salary < 0:
            errors['max_salary'] = "Maximum salary cannot be negative."
        if self.min_salary is not None and self.max_salary is not None and self.min_salary > self.max_salary:
            errors['max_salary'] = "Maximum salary must be greater than or equal to minimum salary."
        if self.min_experience_years is not None and self.min_experience_years < 0:
            errors['min_experience_years'] = "Minimum experience cannot be negative."
        if self.max_experience_years is not None and self.max_experience_years < 0:
            errors['max_experience_years'] = "Maximum experience cannot be negative."
        if (
            self.min_experience_years is not None
            and self.max_experience_years is not None
            and self.min_experience_years > self.max_experience_years
        ):
            errors['max_experience_years'] = "Maximum experience must be greater than or equal to minimum experience."
        if self.is_verified and not (self.source and self.source_url):
            errors['is_verified'] = "Add a source and source URL before marking this job verified."
        if self.application_method == self.ApplicationMethod.EMAIL and not self.application_email:
            errors['application_email'] = "An official application email is required for email applications."
        if self.application_method == self.ApplicationMethod.EXTERNAL_URL and not self.application_url:
            errors['application_url'] = "A verified application URL is required for external applications."
        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    @property
    def company_display_name(self):
        if self.company_id:
            return self.company.name
        return self.employer_name.strip() or "Employer undisclosed"

    @property
    def posted_at(self):
        return self.published_at or self.created_at

    @property
    def is_new(self):
        posted_at = self.posted_at
        if posted_at is None:
            return False
        age = timezone.now() - posted_at
        return timedelta(0) <= age < timedelta(days=3)

    @property
    def has_job_posting_schema(self):
        return bool(
            self.status == self.Status.PUBLISHED
            and self.is_active_for_application
            and self.is_verified
            and self.company_id
            and self.source_url
            and self.location
            and self.location_country
            and self.posted_at
        )

    @property
    def salary_display(self):
        """Format salary clearly for the UI."""
        if self.hide_salary:
            return "Best in Industry"
        if self.min_salary is not None and self.max_salary is not None:
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
        if self.status != self.Status.PUBLISHED:
            return False
        if self.published_at and self.published_at > timezone.now():
            return False
        if self.application_deadline and self.application_deadline < timezone.now().date():
            return False
        return True

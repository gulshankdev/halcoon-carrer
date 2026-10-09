from django.db import models


class EmployerEnquiry(models.Model):
    """
    Staffing and recruitment hiring request submitted by an employer.
    """
    STATUS_CHOICES = [
        ('New', 'New Enquiry'),
        ('Contacted', 'Contacted / Follow-up'),
        ('In Discussion', 'In Discussion / Requirement Analysis'),
        ('Agreement Signed', 'Service Agreement Signed'),
        ('Closed', 'Fulfilled / Closed'),
    ]

    contact_person = models.CharField(max_length=150, help_text="Name of HR / Hiring Manager")
    company_name = models.CharField(max_length=200, help_text="Registered or trading company name")
    email = models.EmailField(help_text="Official business email address")
    phone = models.CharField(max_length=20, help_text="Direct business phone or mobile number")
    hiring_requirements = models.TextField(
        help_text="Specify job roles, departments, or positions needed"
    )
    vacancies_count = models.PositiveIntegerField(
        default=1,
        help_text="Estimated number of openings to fulfill"
    )
    required_skills = models.TextField(
        blank=True,
        help_text="Key technical, commercial, or operational skill requirements"
    )
    message = models.TextField(
        blank=True,
        help_text="Additional instructions, budget parameters, or timeline"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='New'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employer Enquiry"
        verbose_name_plural = "Employer Enquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} ({self.contact_person}) - {self.vacancies_count} vacancy(ies)"

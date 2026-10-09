from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from jobs.models import Job, Category
from .forms import ContactForm


def home_view(request):
    """
    Homepage view for HALCON CAREER.
    Dynamically loads featured vacancies, latest jobs, and active categories from DB.
    """
    featured_jobs = Job.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')[:6]

    latest_jobs = Job.objects.filter(
        is_published=True
    ).select_related('category').order_by('-created_at')[:6]

    categories = Category.objects.filter(
        active=True
    ).annotate(
        active_jobs_count=Count('jobs', filter=Q(jobs__is_published=True))
    ).order_by('name')[:8]

    # Distinct locations for search dropdown
    locations = Job.objects.filter(
        is_published=True
    ).values_list('location', flat=True).distinct()[:10]

    context = {
        'featured_jobs': featured_jobs,
        'latest_jobs': latest_jobs,
        'categories': categories,
        'locations': locations,
        'employment_types': Job.EMPLOYMENT_TYPE_CHOICES,
    }
    return render(request, 'core/index.html', context)


def about_view(request):
    """About Us page outlining recruitment philosophy, mission, and candidate/employer approach."""
    return render(request, 'core/about.html')


def services_view(request):
    """Recruitment Services page showcasing permanent staffing, fresher & experienced hiring."""
    return render(request, 'core/services.html')


def contact_view(request):
    """Contact Us page handling general public inquiries and displaying office location."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you for contacting HALCON CAREER. Our recruitment team has received your message and will respond shortly."
            )
            return redirect('core:contact')
        else:
            messages.error(
                request,
                "There was an error with your submission. Please check the form fields and try again."
            )
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


def privacy_policy_view(request):
    """Legal: Privacy Policy."""
    return render(request, 'core/privacy_policy.html')


def terms_of_service_view(request):
    """Legal: Terms and Conditions."""
    return render(request, 'core/terms_of_service.html')


def candidate_consent_view(request):
    """Legal: Candidate Consent and Resume Handling Policy."""
    return render(request, 'core/candidate_consent.html')


def health_check_view(request):
    """
    Health check endpoint for container orchestrators and monitoring (Render / AWS / K8s).
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'HALCON CAREER Recruitment Platform',
        'timestamp': timezone.now().isoformat(),
        'database': 'operational',
    })


def robots_txt_view(request):
    """Dynamic robots.txt response."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /applications/download-resume/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# Custom HTTP error views
def custom_bad_request_view(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def custom_permission_denied_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def custom_page_not_found_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def custom_server_error_view(request):
    return render(request, 'errors/500.html', status=500)

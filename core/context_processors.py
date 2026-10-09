"""
Context processor providing company branding, contact details,
and navigation data across all templates.
"""
from django.conf import settings


def company_context(request):
    """Provides HALCON CAREER corporate metadata and contact details globally."""
    # Lazy import to avoid circular dependencies during initialization
    try:
        from jobs.models import Category, Job
        categories = Category.objects.filter(active=True).order_by('name')[:8]
        total_active_jobs = Job.objects.filter(is_published=True).count()
    except Exception:
        categories = []
        total_active_jobs = 0

    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'HALCON CAREER'),
        'COMPANY_TAGLINE': getattr(settings, 'COMPANY_TAGLINE', 'Connecting Talent. Creating Opportunities.'),
        'COMPANY_ADDRESS': getattr(settings, 'COMPANY_ADDRESS', 'SCO 12–13, 2nd Floor, Phase 11, Mohali, Punjab – 160065'),
        'COMPANY_PHONE_PRIMARY': getattr(settings, 'COMPANY_PHONE_PRIMARY', '+91 9216033444'),
        'COMPANY_PHONE_SECONDARY': getattr(settings, 'COMPANY_PHONE_SECONDARY', '+91 8699000984'),
        'COMPANY_EMAIL': getattr(settings, 'COMPANY_EMAIL', 'contact@halconcareer.com'),
        'COMPANY_HOURS': getattr(settings, 'COMPANY_HOURS', 'Mon - Fri: 9:30 AM – 6:30 PM | Sat: 10:00 AM – 2:00 PM'),
        'GOOGLE_MAPS_EMBED_URL': getattr(settings, 'GOOGLE_MAPS_EMBED_URL', ''),
        'NAV_CATEGORIES': categories,
        'GLOBAL_ACTIVE_JOBS_COUNT': total_active_jobs,
    }


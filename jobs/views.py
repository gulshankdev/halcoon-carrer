from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Job, Category
from applications.models import JobApplication


def job_list_view(request):
    """
    Search and filter published job vacancies.
    Supports filtering by keyword, category, location, employment type, and experience.
    """
    queryset = Job.objects.filter(is_published=True).select_related('category').order_by('-created_at')

    # Query params
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    location = request.GET.get('location', '').strip()
    employment_type = request.GET.get('type', '').strip()
    experience = request.GET.get('experience', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(required_skills__icontains=q) |
            Q(responsibilities__icontains=q) |
            Q(employer_name__icontains=q)
        )

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if location:
        queryset = queryset.filter(location__icontains=location)

    if employment_type:
        queryset = queryset.filter(employment_type=employment_type)

    if experience:
        queryset = queryset.filter(experience_requirements=experience)

    if sort_by == 'oldest':
        queryset = queryset.order_by('created_at')
    else:
        queryset = queryset.order_by('-created_at')

    # Pagination: 9 jobs per page
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    categories = Category.objects.filter(active=True).order_by('name')
    locations = Job.objects.filter(is_published=True).values_list('location', flat=True).distinct()

    # Determine if any filter is active
    has_active_filters = bool(q or category_slug or location or employment_type or experience)

    context = {
        'page_obj': page_obj,
        'total_jobs_count': queryset.count(),
        'categories': categories,
        'locations': locations,
        'employment_types': Job.EMPLOYMENT_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
        'current_q': q,
        'current_category': category_slug,
        'current_location': location,
        'current_type': employment_type,
        'current_experience': experience,
        'current_sort': sort_by,
        'has_active_filters': has_active_filters,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, slug):
    """
    Detailed job vacancy view with requirement breakdown, related jobs, and apply CTA.
    Only published jobs are accessible to the public (staff can preview unpublished).
    """
    if request.user.is_staff:
        job = get_object_or_404(Job.objects.select_related('category'), slug=slug)
    else:
        job = get_object_or_404(Job.objects.select_related('category'), slug=slug, is_published=True)

    # Check if the authenticated candidate has already applied
    already_applied = False
    application_record = None
    if request.user.is_authenticated:
        application_record = JobApplication.objects.filter(
            candidate=request.user,
            job=job
        ).first()
        already_applied = application_record is not None

    # Related vacancies in same category or general active
    related_jobs = Job.objects.filter(
        is_published=True,
        category=job.category
    ).exclude(id=job.id).order_by('-created_at')[:3]

    context = {
        'job': job,
        'already_applied': already_applied,
        'application_record': application_record,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)

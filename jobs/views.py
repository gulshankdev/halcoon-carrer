from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from .models import Job, Category
from applications.models import JobApplication


def job_list_view(request):
    """
    Search and filter published job vacancies.
    Supports filtering by keyword, category, location, employment type, and experience.
    """
    queryset = Job.objects.open().filter(
        Q(category__isnull=True) | Q(category__active=True)
    ).select_related('category', 'company').order_by('-published_at', '-created_at')

    # Query params
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    location = request.GET.get('location', '').strip()
    employment_type = request.GET.get('type', '').strip()
    experience = request.GET.get('experience', '').strip()
    work_mode = request.GET.get('work_mode', '').strip()
    minimum_salary = request.GET.get('min_salary', '').strip()
    maximum_salary = request.GET.get('max_salary', '').strip()
    minimum_experience = request.GET.get('min_experience', '').strip()
    maximum_experience = request.GET.get('max_experience', '').strip()
    date_posted = request.GET.get('date_posted', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(required_skills__icontains=q) |
            Q(responsibilities__icontains=q) |
            Q(employer_name__icontains=q) |
            Q(company__name__icontains=q)
        )

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if location:
        queryset = queryset.filter(location__icontains=location)

    if employment_type:
        queryset = queryset.filter(employment_type=employment_type)

    if experience:
        queryset = queryset.filter(experience_requirements=experience)

    if work_mode in Job.WorkMode.values:
        queryset = queryset.filter(work_mode=work_mode)

    def valid_amount(value):
        try:
            amount = Decimal(value)
            return amount if amount.is_finite() and amount >= 0 else None
        except (InvalidOperation, ValueError):
            return None

    min_salary_value = valid_amount(minimum_salary) if minimum_salary else None
    max_salary_value = valid_amount(maximum_salary) if maximum_salary else None
    min_experience_value = valid_amount(minimum_experience) if minimum_experience else None
    max_experience_value = valid_amount(maximum_experience) if maximum_experience else None
    if minimum_salary and min_salary_value is None:
        minimum_salary = ''
    if maximum_salary and max_salary_value is None:
        maximum_salary = ''
    if minimum_experience and min_experience_value is None:
        minimum_experience = ''
    if maximum_experience and max_experience_value is None:
        maximum_experience = ''
    if min_salary_value is not None:
        queryset = queryset.filter(max_salary__gte=min_salary_value)
    if max_salary_value is not None:
        queryset = queryset.filter(min_salary__lte=max_salary_value)
    if min_experience_value is not None:
        queryset = queryset.filter(
            Q(max_experience_years__gte=min_experience_value) |
            Q(max_experience_years__isnull=True)
        )
    if max_experience_value is not None:
        queryset = queryset.filter(
            Q(min_experience_years__lte=max_experience_value) |
            Q(min_experience_years__isnull=True)
        )

    posted_ranges = {'24h': 1, '7d': 7, '30d': 30}
    if date_posted in posted_ranges:
        cutoff = timezone.now() - timedelta(days=posted_ranges[date_posted])
        queryset = queryset.filter(
            Q(published_at__gte=cutoff) |
            Q(published_at__isnull=True, created_at__gte=cutoff)
        )

    if sort_by == 'oldest':
        queryset = queryset.order_by('published_at', 'created_at')
    else:
        queryset = queryset.order_by('-published_at', '-created_at')

    # Pagination: 9 jobs per page
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    categories = Category.objects.filter(active=True).order_by('name')
    locations = Job.objects.open().values_list('location', flat=True).distinct()
    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)

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
        'has_active_filters': has_active_filters or bool(
            work_mode or minimum_salary or maximum_salary or minimum_experience
            or maximum_experience or date_posted
        ),
        'work_modes': Job.WorkMode.choices,
        'current_work_mode': work_mode,
        'current_min_salary': minimum_salary,
        'current_max_salary': maximum_salary,
        'current_min_experience': minimum_experience,
        'current_max_experience': maximum_experience,
        'current_date_posted': date_posted,
        'pagination_query': pagination_params.urlencode(),
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
        job = get_object_or_404(
            Job.objects.published().select_related('category', 'company').filter(
                Q(category__isnull=True) | Q(category__active=True)
            ),
            slug=slug,
        )

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
    related_jobs = Job.objects.open().filter(
        category=job.category
    ).exclude(id=job.id).order_by('-created_at')[:3]

    context = {
        'job': job,
        'already_applied': already_applied,
        'application_record': application_record,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)


def category_jobs_view(request, slug):
    category = get_object_or_404(Category, slug=slug, active=True)
    request.GET = request.GET.copy()
    request.GET['category'] = category.slug
    return job_list_view(request)

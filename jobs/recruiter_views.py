import hashlib
import mimetypes
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.storage import get_resume_path
from applications.models import JobApplication
from employers.models import Company, EmployerEnquiry
from .forms import CategoryForm, CompanyForm, JobForm, RecruiterLoginForm
from .models import Category, Job
from .permissions import can_manage_recruiter, recruiter_required


LOGIN_LIMIT = 5
LOGIN_WINDOW_SECONDS = 15 * 60


def recruiter_login_view(request):
    if request.user.is_authenticated and can_manage_recruiter(request.user):
        return redirect('recruiter:dashboard')

    form = RecruiterLoginForm(request.POST or None)
    if request.method == 'POST':
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        cache_token = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()
        failures_key = f'recruiter-login-failures:{cache_token}'
        locked_key = f'recruiter-login-locked:{cache_token}'
        if cache.get(locked_key):
            form.add_error(None, 'Too many unsuccessful attempts. Try again in 15 minutes.')
        elif form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and can_manage_recruiter(user):
                login(request, user)
                cache.delete(failures_key)
                cache.delete(locked_key)
                return redirect('recruiter:dashboard')

            failures = cache.get(failures_key, 0)
            if failures:
                try:
                    failures = cache.incr(failures_key)
                except ValueError:
                    failures = LOGIN_LIMIT
            else:
                failures = 1
                cache.set(failures_key, failures, LOGIN_WINDOW_SECONDS)
            if failures >= LOGIN_LIMIT:
                cache.set(locked_key, True, LOGIN_WINDOW_SECONDS)
            form.add_error(None, 'Invalid username or password, or this account is not authorized.')

    return render(request, 'recruiter/login.html', {'form': form})


@recruiter_required
def recruiter_dashboard_view(request):
    jobs = Job.objects.all()
    context = {
        'total_jobs': jobs.count(),
        'published_jobs': jobs.filter(status=Job.Status.PUBLISHED).count(),
        'draft_jobs': jobs.filter(status=Job.Status.DRAFT).count(),
        'closed_jobs': jobs.filter(status=Job.Status.CLOSED).count(),
        'applications_count': JobApplication.objects.count(),
        'recent_jobs': jobs.select_related('company', 'category')[:8],
        'recent_applications': JobApplication.objects.select_related(
            'job', 'candidate'
        )[:8],
    }
    return render(request, 'recruiter/dashboard.html', context)


@recruiter_required
def recruiter_job_list_view(request):
    queryset = Job.objects.select_related('company', 'category').annotate(
        application_count=Count('applications')
    ).order_by('-created_at')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    category = request.GET.get('category', '').strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(employer_name__icontains=query) |
            Q(company__name__icontains=query) | Q(location__icontains=query)
        )
    if status in Job.Status.values:
        queryset = queryset.filter(status=status)
    if category.isdigit():
        queryset = queryset.filter(category_id=category)
    page_obj = Paginator(queryset, 20).get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    return render(request, 'recruiter/jobs.html', {
        'page_obj': page_obj,
        'categories': Category.objects.order_by('name'),
        'statuses': Job.Status.choices,
        'current_q': query,
        'current_status': status,
        'current_category': category,
        'pagination_query': query_params.urlencode(),
    })


def _save_job_company(form, job):
    company_name = form.cleaned_data.get('company_name', '').strip()
    company = form.cleaned_data.get('company')
    logo = form.cleaned_data.get('company_logo')
    if company_name:
        company, _ = Company.objects.get_or_create(name=company_name)
    if company:
        if logo:
            company.logo = logo
            company.save(update_fields=['logo', 'updated_at'])
        job.company = company
        job.employer_name = company.name


def _job_form_response(request, form, heading, job=None):
    return render(request, 'recruiter/job_form.html', {
        'form': form,
        'heading': heading,
        'job': job,
        'categories_url': 'recruiter:category_add',
    })


@recruiter_required
def recruiter_job_add_view(request):
    form = JobForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        _save_job_company(form, job)
        job.save()
        messages.success(request, f'"{job.title}" was saved successfully.')
        if job.status == Job.Status.PUBLISHED and job.is_active_for_application:
            messages.info(request, 'The job is live on the public jobs portal.')
        return redirect('recruiter:jobs')
    return _job_form_response(request, form, 'Add New Job')


@recruiter_required
def recruiter_job_edit_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    form = JobForm(request.POST or None, request.FILES or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        _save_job_company(form, job)
        job.save()
        messages.success(request, f'"{job.title}" was updated successfully.')
        return redirect('recruiter:jobs')
    return _job_form_response(request, form, 'Edit Job', job)


@recruiter_required
def recruiter_job_preview_view(request, pk):
    job = get_object_or_404(Job.objects.select_related('category', 'company'), pk=pk)
    related_jobs = Job.objects.open().filter(category=job.category).exclude(pk=job.pk)[:3]
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'already_applied': False,
        'application_record': None,
        'related_jobs': related_jobs,
        'recruiter_preview': True,
    })


@recruiter_required
@require_POST
def recruiter_job_status_view(request, pk, status):
    if status not in Job.Status.values:
        raise Http404
    job = get_object_or_404(Job, pk=pk)
    job.status = status
    if status == Job.Status.PUBLISHED and job.published_at is None:
        job.published_at = timezone.now()
    job.save(update_fields=['status', 'published_at'])
    messages.success(request, f'"{job.title}" status changed to {status.lower()}.')
    return redirect('recruiter:jobs')


@recruiter_required
def recruiter_job_delete_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect('recruiter:jobs')
    return render(request, 'recruiter/job_delete.html', {'job': job})


@recruiter_required
@require_POST
def recruiter_job_bulk_action_view(request):
    selected = request.POST.getlist('jobs')
    jobs = Job.objects.filter(pk__in=selected)
    action = request.POST.get('action')
    if action in Job.Status.values:
        jobs.update(status=action, is_published=(action == Job.Status.PUBLISHED))
        messages.success(request, f'{jobs.count()} selected job(s) were updated.')
    elif action == 'delete':
        count = jobs.count()
        jobs.delete()
        messages.success(request, f'{count} selected job(s) were deleted.')
    else:
        messages.error(request, 'Choose a valid bulk action.')
    return redirect('recruiter:jobs')


@recruiter_required
def recruiter_applications_view(request):
    queryset = JobApplication.objects.select_related('job', 'candidate').order_by('-submitted_at')
    status = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()
    if status in dict(JobApplication.STATUS_CHOICES):
        queryset = queryset.filter(status=status)
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query) | Q(email__icontains=query) |
            Q(job__title__icontains=query)
        )
    page_obj = Paginator(queryset, 20).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'recruiter/applications.html', {
        'page_obj': page_obj,
        'statuses': JobApplication.STATUS_CHOICES,
        'current_status': status,
        'current_q': query,
        'pagination_query': params.urlencode(),
    })


@recruiter_required
@require_POST
def recruiter_application_status_view(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    status = request.POST.get('status')
    if status not in dict(JobApplication.STATUS_CHOICES):
        messages.error(request, 'Choose a valid application status.')
    else:
        application.status = status
        application.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Application status updated.')
    return redirect('recruiter:applications')


@recruiter_required
def recruiter_categories_view(request):
    return render(request, 'recruiter/categories.html', {
        'categories': Category.objects.annotate(job_count=Count('jobs')).order_by('name')
    })


@recruiter_required
def recruiter_category_add_view(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        category = form.save()
        messages.success(request, f'Category "{category.name}" was created.')
        return redirect('recruiter:categories')
    return render(request, 'recruiter/simple_form.html', {'form': form, 'heading': 'Add Job Category'})


@recruiter_required
def recruiter_category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated.')
        return redirect('recruiter:categories')
    return render(request, 'recruiter/simple_form.html', {'form': form, 'heading': 'Edit Job Category'})


@recruiter_required
def recruiter_companies_view(request):
    return render(request, 'recruiter/companies.html', {
        'companies': Company.objects.annotate(job_count=Count('jobs')).order_by('name')
    })


@recruiter_required
def recruiter_company_add_view(request):
    form = CompanyForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Company saved successfully.')
        return redirect('recruiter:companies')
    return render(request, 'recruiter/simple_form.html', {'form': form, 'heading': 'Add Company'})


@recruiter_required
def recruiter_company_edit_view(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Company updated successfully.')
        return redirect('recruiter:companies')
    return render(request, 'recruiter/simple_form.html', {'form': form, 'heading': 'Edit Company'})


@recruiter_required
def recruiter_enquiries_view(request):
    return render(request, 'recruiter/enquiries.html', {
        'enquiries': EmployerEnquiry.objects.order_by('-created_at')
    })


@recruiter_required
@require_POST
def recruiter_logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out of the recruiter dashboard.')
    return redirect('recruiter:login')


@recruiter_required
def recruiter_resume_view(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if not application.resume_file:
        raise Http404('Resume file not found.')
    file_path = get_resume_path(application.resume_file)
    if file_path is None:
        raise Http404('Resume file not found.')
    content_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type or 'application/octet-stream',
        as_attachment=True,
        filename=file_path.name,
    )

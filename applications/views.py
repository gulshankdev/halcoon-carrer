import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from jobs.models import Job
from .models import JobApplication
from .forms import JobApplicationForm
from accounts.models import CandidateProfile


@login_required
def apply_view(request, slug):
    """
    Candidate application submission for a specific published vacancy.
    Enforces login, checks for duplicate applications, and validates uploaded resume.
    """
    job = get_object_or_404(Job, slug=slug, is_published=True)

    # Check if job is still open for application
    if not job.is_active_for_application:
        messages.error(request, "This vacancy is no longer accepting new applications.")
        return redirect('jobs:job_detail', slug=job.slug)

    # Duplicate application check
    existing_application = JobApplication.objects.filter(
        candidate=request.user,
        job=job
    ).first()
    if existing_application:
        messages.info(
            request,
            f"You have already applied for '{job.title}'. Your current status is: {existing_application.status}."
        )
        return redirect('applications:my_applications')

    # Candidate profile for pre-filling and checking existing resume
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
    has_profile_resume = bool(profile.resume)

    if request.method == 'POST':
        form = JobApplicationForm(
            request.POST,
            request.FILES,
            has_profile_resume=has_profile_resume
        )
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job

            # If candidate opted to reuse profile resume and didn't upload a new one
            if form.cleaned_data.get('use_existing_resume') and has_profile_resume and not request.FILES.get('resume_file'):
                # Copy file content from profile resume
                resume_file_path = profile.resume.path
                if os.path.exists(resume_file_path):
                    with open(resume_file_path, 'rb') as f:
                        filename = os.path.basename(resume_file_path)
                        application.resume_file.save(filename, ContentFile(f.read()), save=False)

            application.save()
            messages.success(
                request,
                f"Application submitted successfully for '{job.title}'! Our recruitment team will review your profile."
            )
            return redirect('applications:my_applications')
        else:
            messages.error(request, "Please review and correct the errors below.")
    else:
        # Prepopulate with candidate user credentials
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone,
            'use_existing_resume': has_profile_resume,
        }
        form = JobApplicationForm(initial=initial_data, has_profile_resume=has_profile_resume)

    context = {
        'job': job,
        'form': form,
        'has_profile_resume': has_profile_resume,
        'profile': profile,
    }
    return render(request, 'applications/apply.html', context)


@login_required
def my_applications_view(request):
    """
    Candidate's dashboard displaying all their previous job applications and statuses.
    """
    applications_list = JobApplication.objects.filter(
        candidate=request.user
    ).select_related('job', 'job__category').order_by('-submitted_at')

    context = {
        'applications': applications_list,
        'total_count': applications_list.count(),
    }
    return render(request, 'applications/my_applications.html', context)


@login_required
def download_application_resume(request, application_id):
    """
    Secure access-controlled resume download endpoint.
    Only authorized staff recruiters or the candidate owner can download the submitted resume.
    """
    application = get_object_or_404(JobApplication, id=application_id)

    # Permission check
    if not (request.user.is_staff or request.user == application.candidate):
        raise PermissionDenied("You do not have permission to access this candidate resume.")

    if not application.resume_file:
        raise Http404("Resume file not found.")

    file_path = application.resume_file.path
    if not os.path.exists(file_path):
        raise Http404("The requested file was not found on server storage.")

    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    filename = os.path.basename(file_path)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

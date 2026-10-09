import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from .forms import (
    CandidateRegistrationForm,
    CandidateLoginForm,
    UserUpdateForm,
    CandidateProfileForm
)
from .models import CandidateProfile
from applications.models import JobApplication


def register_view(request):
    """Candidate account registration."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to HALCON CAREER, {user.first_name}! Your candidate account has been created."
            )
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = CandidateRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Candidate login view."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CandidateLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:profile')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CandidateLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Candidate logout view."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out securely.")
        return redirect('core:home')
    # If GET, confirm logout or redirect
    return render(request, 'accounts/logout_confirm.html')


@login_required
def profile_view(request):
    """Candidate profile view and management."""
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = CandidateProfileForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your candidate profile has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please review the errors in the form.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = CandidateProfileForm(instance=profile)

    # Candidate's active applications
    recent_applications = JobApplication.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-submitted_at')[:5]

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'recent_applications': recent_applications,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def download_profile_resume(request, user_id):
    """
    Secure permission-checked download of candidate profile resume.
    Ensures resumes are NEVER publicly exposed without authentication and authorization.
    """
    profile = get_object_or_404(CandidateProfile, user__id=user_id)

    # Permission check: must be staff or the candidate themselves
    if not (request.user.is_staff or request.user == profile.user):
        raise PermissionDenied("You do not have permission to access this candidate resume.")

    if not profile.resume:
        raise Http404("No resume uploaded for this candidate.")

    file_path = profile.resume.path
    if not os.path.exists(file_path):
        raise Http404("Resume file not found on server storage.")

    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    filename = os.path.basename(file_path)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

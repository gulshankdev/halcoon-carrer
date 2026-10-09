import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'job_title',
        'email',
        'phone',
        'status',
        'submitted_at',
        'download_resume_link',
    )
    list_filter = ('status', 'submitted_at', 'job__category')
    search_fields = (
        'full_name',
        'email',
        'phone',
        'job__title',
        'job__employer_name',
        'cover_letter',
    )
    readonly_fields = ('candidate', 'job', 'submitted_at', 'updated_at', 'download_resume_link')
    list_editable = ('status',)
    date_hierarchy = 'submitted_at'
    actions = [
        'mark_under_review',
        'mark_shortlisted',
        'mark_interview',
        'mark_selected',
        'mark_rejected',
        'export_applications_to_csv',
    ]

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Applied Position'

    def download_resume_link(self, obj):
        if obj.resume_file:
            url = reverse('applications:download_resume', args=[obj.id])
            return format_html('<a href="{}" target="_blank" class="button">Download Resume</a>', url)
        return "No resume attached"
    download_resume_link.short_description = 'Resume File'

    # Admin actions for bulk status updates
    @admin.action(description="Mark selected as Under Review")
    def mark_under_review(self, request, queryset):
        queryset.update(status='Under Review')

    @admin.action(description="Mark selected as Shortlisted")
    def mark_shortlisted(self, request, queryset):
        queryset.update(status='Shortlisted')

    @admin.action(description="Mark selected as Interview")
    def mark_interview(self, request, queryset):
        queryset.update(status='Interview')

    @admin.action(description="Mark selected as Selected")
    def mark_selected(self, request, queryset):
        queryset.update(status='Selected')

    @admin.action(description="Mark selected as Rejected")
    def mark_rejected(self, request, queryset):
        queryset.update(status='Rejected')

    @admin.action(description="Export selected applications to CSV")
    def export_applications_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="halcon_career_applications.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Candidate Name', 'Email', 'Phone', 'Job Title', 'Status', 'Submitted Date'])

        for app in queryset:
            writer.writerow([
                app.id,
                app.full_name,
                app.email,
                app.phone,
                app.job.title,
                app.status,
                app.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return response

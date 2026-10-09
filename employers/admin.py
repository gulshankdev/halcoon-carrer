import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import EmployerEnquiry


@admin.register(EmployerEnquiry)
class EmployerEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'contact_person',
        'email',
        'phone',
        'vacancies_count',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'company_name',
        'contact_person',
        'email',
        'phone',
        'hiring_requirements',
        'required_skills',
        'message',
    )
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    actions = ['mark_contacted', 'mark_in_discussion', 'mark_closed', 'export_enquiries_to_csv']

    @admin.action(description="Mark selected enquiries as Contacted")
    def mark_contacted(self, request, queryset):
        queryset.update(status='Contacted')

    @admin.action(description="Mark selected enquiries as In Discussion")
    def mark_in_discussion(self, request, queryset):
        queryset.update(status='In Discussion')

    @admin.action(description="Mark selected enquiries as Closed")
    def mark_closed(self, request, queryset):
        queryset.update(status='Closed')

    @admin.action(description="Export selected enquiries to CSV")
    def export_enquiries_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="halcon_career_employer_enquiries.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID',
            'Company Name',
            'Contact Person',
            'Email',
            'Phone',
            'Vacancies Count',
            'Hiring Requirements',
            'Status',
            'Date Created',
        ])
        for enq in queryset:
            writer.writerow([
                enq.id,
                enq.company_name,
                enq.contact_person,
                enq.email,
                enq.phone,
                enq.vacancies_count,
                enq.hiring_requirements,
                enq.status,
                enq.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return response

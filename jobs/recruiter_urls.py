from django.urls import path

from . import recruiter_views

app_name = 'recruiter'

urlpatterns = [
    path('login/', recruiter_views.recruiter_login_view, name='login'),
    path('logout/', recruiter_views.recruiter_logout_view, name='logout'),
    path('dashboard/', recruiter_views.recruiter_dashboard_view, name='dashboard'),
    path('jobs/', recruiter_views.recruiter_job_list_view, name='jobs'),
    path('jobs/add/', recruiter_views.recruiter_job_add_view, name='job_add'),
    path('jobs/<int:pk>/edit/', recruiter_views.recruiter_job_edit_view, name='job_edit'),
    path('jobs/<int:pk>/preview/', recruiter_views.recruiter_job_preview_view, name='job_preview'),
    path('jobs/<int:pk>/status/<str:status>/', recruiter_views.recruiter_job_status_view, name='job_status'),
    path('jobs/<int:pk>/delete/', recruiter_views.recruiter_job_delete_view, name='job_delete'),
    path('jobs/bulk-action/', recruiter_views.recruiter_job_bulk_action_view, name='job_bulk_action'),
    path('applications/', recruiter_views.recruiter_applications_view, name='applications'),
    path('applications/<int:pk>/status/', recruiter_views.recruiter_application_status_view, name='application_status'),
    path('applications/<int:pk>/resume/', recruiter_views.recruiter_resume_view, name='resume'),
    path('categories/', recruiter_views.recruiter_categories_view, name='categories'),
    path('categories/add/', recruiter_views.recruiter_category_add_view, name='category_add'),
    path('categories/<int:pk>/edit/', recruiter_views.recruiter_category_edit_view, name='category_edit'),
    path('companies/', recruiter_views.recruiter_companies_view, name='companies'),
    path('companies/add/', recruiter_views.recruiter_company_add_view, name='company_add'),
    path('companies/<int:pk>/edit/', recruiter_views.recruiter_company_edit_view, name='company_edit'),
    path('enquiries/', recruiter_views.recruiter_enquiries_view, name='enquiries'),
]

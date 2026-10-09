from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<slug:slug>/', views.apply_view, name='apply'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('resume/<int:application_id>/', views.download_application_resume, name='download_resume'),
]


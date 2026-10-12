from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('category/<slug:slug>/', views.category_jobs_view, name='category_jobs'),
    path('<slug:slug>/', views.job_detail_view, name='job_detail'),
]

from django.urls import path

from .api import PublicJobDetailAPIView, PublicJobListAPIView

app_name = 'job_api'

urlpatterns = [
    path('', PublicJobListAPIView.as_view(), name='list'),
    path('<slug:slug>/', PublicJobDetailAPIView.as_view(), name='detail'),
]

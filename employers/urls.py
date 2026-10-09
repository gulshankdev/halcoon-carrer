from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    path('hire-talent/', views.enquiry_view, name='enquiry'),
    path('hire-talent/success/', views.enquiry_success_view, name='enquiry_success'),
]


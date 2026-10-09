from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_of_service_view, name='terms_of_service'),
    path('candidate-consent-policy/', views.candidate_consent_view, name='candidate_consent'),
    path('health/', views.health_check_view, name='health'),
    path('robots.txt', views.robots_txt_view, name='robots_txt'),
]


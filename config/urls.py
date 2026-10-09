"""
URL configuration for HALCON CAREER recruitment platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, JobSitemap

# Configure Django Admin Branding
admin.site.site_header = "HALCON CAREER Recruitment Administration"
admin.site.site_title = "HALCON CAREER Portal Admin"
admin.site.index_title = "Recruitment & Staffing Management Dashboard"

sitemaps = {
    'static': StaticViewSitemap,
    'jobs': JobSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('applications/', include('applications.urls')),
    path('employers/', include('employers.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Error Handlers
handler400 = 'core.views.custom_bad_request_view'
handler403 = 'core.views.custom_permission_denied_view'
handler404 = 'core.views.custom_page_not_found_view'
handler500 = 'core.views.custom_server_error_view'

if settings.DEBUG:
    # Serve static and media during local development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

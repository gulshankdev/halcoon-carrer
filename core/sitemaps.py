from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from jobs.models import Job


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'jobs:job_list', 'core:services', 'core:about', 'core:contact', 'employers:enquiry']

    def location(self, item):
        return reverse(item)


class JobSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Job.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at


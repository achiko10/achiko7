from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'services', 'projects', 'contact']

    def location(self, item):
        return reverse(item)

class ProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return reverse('project_detail', args=[obj.slug])

from django.contrib.sitemaps import Sitemap
from .models import CustomUser

class AthleteSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return CustomUser.objects.filter(user_type='athlete', slug__isnull=False)

    def location(self, obj):
        return f"/atleta/{obj.slug}/"

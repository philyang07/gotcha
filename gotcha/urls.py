"""gotcha URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views

from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap, Sitemap

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'accounts:home',
            'accounts:guide',
            'accounts:login',
            'accounts:register',
            'accounts:create_game',
        ]

    def location(self, item):
        return reverse(item)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': {'static': StaticViewSitemap}},
        name='django.contrib.sitemaps.views.sitemap'),
]

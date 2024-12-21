"""
URL configuration for CampaignNova project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from CampaignNova.settings import base as settings
from django.conf.urls import handler404

handler404 = "home.views.custom_404"
admin.site.site_header = "CampaignNova"
admin.site.site_title = "CampaignNova"
admin.site.index_title = "CampaignNova"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls"), name="home"),
    path("accounts/", include("accounts.urls"), name="accounts"),
    path("blog/", include("blog.urls"), name="blog"),
    path("dashboard/", include("dashboard.urls"), name="dashboard"),
]



# Serve static and media files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

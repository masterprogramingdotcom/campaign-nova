from django.urls import path

from dashboard.views import DashboardHomeView, ProfileView

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="dashboard-home"),
    path("profile/", ProfileView.as_view(), name="profile"),
]

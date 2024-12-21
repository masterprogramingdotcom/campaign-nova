from django.urls import path

from home.views import (
    AboutView,
    ContactView,
    FAQView,
    HomeView,
    PrivacyPolicyView,
    SaveLocationView,
    ServiceView,
    TermsAndConditionView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("save-location/", SaveLocationView.as_view(), name="save_location"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("about/", AboutView.as_view(), name="about"),
    path("service/", ServiceView.as_view(), name="service"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path(
        "terms-and-condition/",
        TermsAndConditionView.as_view(),
        name="terms-and-condition",
    ),
]

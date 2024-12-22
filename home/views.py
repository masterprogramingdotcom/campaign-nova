import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from home.custom import create_or_get_location
from home.models import Contact

# Create your views here.


def custom_404(request, exception):
    return render(request, "404.html", status=404)


class HomeView(View):
    def get(self, request):
        return render(request, "home/index.html")


class ContactView(View):
    def get(self, request):
        return render(request, "home/contact.html")

    def post(self, request):
        try:
            # Create a new Contact instance and save it to the database
            contact = Contact(
                full_name=request.POST.get("fullname"),
                phone=request.POST.get("phone"),
                subject=request.POST.get("subject"),
                comments=request.POST.get("desc"),
            )
            contact.save()

            # Send a success response
            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            # If there was a problem with parsing the JSON, return an error
            return JsonResponse(
                {"success": False, "error": "Invalid JSON data"}, status=400
            )

        except Exception as e:
            # Catch any other exceptions and return an error
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class SaveLocationView(View):
    def get(self, request, *args, **kwargs):
        return redirect("index")

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        system_identifier = data.get(
            "system_identifier", "Unknown"
        )  # Default to 'Unknown' if not provided

        location = create_or_get_location(
            request, latitude, longitude, system_identifier
        )

        return JsonResponse(
            {
                "status": "success",
            }
        )


class AboutView(View):
    def get(self, request):
        return render(request, "home/about.html")


class ServiceView(View):
    def get(self, request):
        return render(request, "home/service.html")


class FAQView(View):
    def get(self, request):
        return render(request, "home/faq.html")


class PrivacyPolicyView(View):
    def get(self, request):
        return render(request, "home/privacy-policy.html")


class TermsAndConditionView(View):
    def get(self, request):
        return render(request, "home/terms-and-condition.html")

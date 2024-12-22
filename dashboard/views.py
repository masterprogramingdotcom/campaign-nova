from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from accounts.models import Profile

# Create your views here.


class DashboardHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "pages/index.html")


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        return render(request, "pages/profile.html", {"profile": profile})

    def post(self, request, *args, **kwargs):
        # Get the user profile
        profile = request.user.profile

        # Update fields from POST data
        profile.gender = request.POST.get("gender")

        # Convert the birth_date from dd/mm/yyyy to YYYY-MM-DD
        birth_date_str = request.POST.get("birth_date")
        if birth_date_str:
            profile.birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()

        profile.mobile_number = request.POST.get("phone_number")
        profile.nationality = request.POST.get("nationality")
        profile.experience = request.POST.get("experience")

        # Handle file uploads
        if request.FILES.get("aadhar_card"):
            profile.aadhar_card = request.FILES["aadhar_card"]
        if request.FILES.get("voter_id_card"):
            profile.voter_id_card = request.FILES["voter_id_card"]
        if request.FILES.get("pan_card"):
            profile.pan_card = request.FILES["pan_card"]

        # Save the profile changes
        profile.save()

        # Optionally update user fields (first_name, last_name)
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")  # Redirect to the same profile page

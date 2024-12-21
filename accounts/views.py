import random
import re

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from accounts.models import Profile, User, UserRole


class RedirectAuthenticatedUserMixin:
    """
    Mixin to redirect authenticated users to the home page.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)


class Register(RedirectAuthenticatedUserMixin, View):
    def get(self, request):
        return render(request, "accounts/register.html")

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        mobile_number = request.POST.get("mobile_number")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        errors = []

        if not first_name or len(first_name) < 2:
            errors.append("First name must be at least 2 characters long.")

        if not last_name or len(last_name) < 2:
            errors.append("Last name must be at least 2 characters long.")

        if not re.match(r"^\d{10}$", mobile_number):
            errors.append("Mobile number must be a 10-digit number.")

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors.append("Invalid email address.")

        if User.objects.filter(mobile_number=mobile_number).exists():
            errors.append("Mobile number is already in use.")

        if User.objects.filter(email=email).exists():
            errors.append("Email is already in use.")

        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if user_type not in UserRole.values:
            errors.append("Invalid user type.")

        if errors:
            return JsonResponse({"status": "error", "messages": errors}, status=400)

        try:
            user = User.objects.create_user(
                mobile_number=mobile_number, email=email, password=password
            )
            user.user_type = user_type
            user.save()

            Profile.objects.create(user=user)

            return JsonResponse(
                {"status": "success", "message": "User registered successfully!"},
                status=201,
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


def send_otp(phone_number):
    otp = random.randint(100000, 999999)
    message = f"Your OTP is {otp}"
    try:
        url = f"https://2factor.in/API/V1/a2f2dd7d-2b67-11ed-9c12-0200cd936042/SMS/{phone_number}/{otp}/OTP1"
        requests.get(url)
        return otp
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None


class VerifyOTP(View):
    def get(self, request):
        username = request.GET.get("username")
        try:
            user = User.objects.get(mobile_number=username)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found."}, status=404)

        profile = Profile.objects.get(user=user)

        if profile.mobile_verified:
            return redirect("index")

        otp = send_otp(username)
        if otp:
            profile.otp = otp
            profile.save()

        return render(request, "accounts/otp_verify.html", {"username": username})

    def post(self, request):
        username = request.POST.get("username")
        otp = request.POST.get("otp")

        try:
            profile = Profile.objects.get(user__mobile_number=username)
        except Profile.DoesNotExist:
            return JsonResponse({"message": "User not found."}, status=404)

        if profile.otp == otp:
            profile.otp = None
            profile.mobile_verified = True
            profile.save()
            return JsonResponse(
                {"message": "OTP verified successfully!", "success": True}
            )
        else:
            return JsonResponse({"message": "Invalid OTP!"}, status=400)


class Login(RedirectAuthenticatedUserMixin, View):
    def get(self, request):
        next_url = request.GET.get("next", "")
        return render(request, "accounts/login.html", {"next": next_url})

    def post(self, request):
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")

        user = authenticate(request, username=mobile_number, password=password)

        if user is not None:
            if user.profile.mobile_verified:
                login(request, user)
                next_url = request.GET.get("next")

                if user.user_type == UserRole.CUSTOMER:
                    messages.success(request, "Welcome to the customer dashboard.")
                    return redirect(next_url or "index")
                elif user.user_type == UserRole.VENDOR:
                    messages.success(request, "Welcome to the vendor dashboard.")
                    return redirect(next_url or "vendor-dashboard")
            else:
                messages.warning(
                    request,
                    "Your mobile number is not verified. Please verify to continue.",
                )
                return redirect(f"../../accounts/otp-verify?username={mobile_number}")
        else:
            messages.error(request, "Invalid mobile number or password.")
            return render(request, "accounts/login.html")


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("index")

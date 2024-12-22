import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from accounts.models import Profile, User, UserRole
from accounts.utility import send_otp


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
        return render(request, "register.html")

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

        if User.objects.filter(mobile_number=mobile_number).exists():
            return JsonResponse(
                {"status": "error", "message": "Mobile number already registered."},
                status=400,
            )

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


class VerifyOTP(View):
    def get(self, request):
        mobile_number = request.GET.get("mobile_number")
        try:
            user = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found."}, status=404)

        profile = Profile.objects.get(user=user)

        if profile.mobile_verified:
            return redirect("index")

        otp = send_otp(mobile_number)
        if otp:
            profile.otp = otp
            profile.save()

        return render(request, "otp_verify.html", {"mobile_number": mobile_number})

    def post(self, request):
        mobile_number = request.POST.get("mobile_number")
        otp = request.POST.get("otp")

        try:
            profile = Profile.objects.get(user__mobile_number=mobile_number)
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


class Login(View):
    def get(self, request):
        next_url = request.GET.get("next", "")
        return render(request, "login.html", {"next": next_url})

    def post(self, request):
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "")

        user = authenticate(request, mobile_number=mobile_number, password=password)

        if user is not None:
            if user.profile.mobile_verified:
                login(request, user)

                redirect_url = next_url or (
                    "index"
                    if user.user_type == UserRole.CUSTOMER
                    else "vendor-dashboard"
                )
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Login successful.",
                        "redirect_url": redirect_url,
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Mobile number not verified. Redirecting to OTP verification.",
                        "redirect_url": f"../otp-verify?mobile_number={mobile_number}",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {"success": False, "message": "Invalid mobile number or password."},
                status=400,
            )


class ForgotPassword(View):
    def get(self, request):
        if request.is_authenticated:
            return redirect("/")
        return render(request, "forgot_password.html")

    def post(self, request):
        mobile_number = request.POST.get("mobile_number")

        try:
            user = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Mobile number not registered."},
                status=400,
            )

        try:
            otp = send_otp(mobile_number)
            if otp:
                user.profile.otp = otp
                user.profile.save()
                return JsonResponse(
                    {"success": True, "message": "OTP sent to your mobile number."}
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Failed to send OTP. Please try again later.",
                    },
                    status=500,
                )
        except Exception as e:
            print(f"Error in ForgotPassword: {e}")
            return JsonResponse(
                {
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
                status=500,
            )


class VerifyOTPAndResetPassword(View):
    def get(self, request):
        if request.is_authenticated:
            return redirect("/")

        return render(request, "reset_password.html")

    def post(self, request):
        mobile_number = request.POST.get("mobile_number")
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        try:
            user_profile = Profile.objects.get(user__mobile_number=mobile_number)
        except Profile.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Invalid mobile number."}, status=400
            )

        if user_profile.otp == otp:
            user_profile.otp = None
            user_profile.save()

            user = user_profile.user
            user.password = make_password(new_password)
            user.save()

            return JsonResponse(
                {"success": True, "message": "Password reset successfully."}
            )
        else:
            return JsonResponse(
                {"success": False, "message": "Invalid OTP."}, status=400
            )


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("index")

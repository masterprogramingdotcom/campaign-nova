from django.urls import path

from accounts.views import Login, Logout, Register, VerifyOTP

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("otp-verify", VerifyOTP.as_view(), name="otp-verify"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
]

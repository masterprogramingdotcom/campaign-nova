from django.urls import path

from accounts.views import (
    ForgotPassword,
    Login,
    Logout,
    Register,
    VerifyOTP,
    VerifyOTPAndResetPassword,
)

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("otp-verify", VerifyOTP.as_view(), name="otp-verify"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("forgot-password/", ForgotPassword.as_view(), name="forgot-password"),
    path("reset-password/", VerifyOTPAndResetPassword.as_view(), name="reset-password"),
]

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import OTPRequestView, OTPVerifyView, MeView, DeviceRegisterView

urlpatterns = [
    path("otp/request/", OTPRequestView.as_view(), name="otp-request"),
    path("otp/request", OTPRequestView.as_view()),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path("otp/verify", OTPVerifyView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/refresh", TokenRefreshView.as_view()),
    path("me/", MeView.as_view(), name="me"),
    path("me", MeView.as_view()),
    path("devices/", DeviceRegisterView.as_view(), name="devices"),
    path("devices", DeviceRegisterView.as_view()),
]

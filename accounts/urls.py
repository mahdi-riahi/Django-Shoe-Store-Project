from django.urls import path

from . import views


app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('verify_phone/', views.verify_phone_view, name='verify_phone'),
    path('resend_code/', views.resend_verification_code_view, name='resend_code'),
    path('login/', views.login_view, name='login'),
]

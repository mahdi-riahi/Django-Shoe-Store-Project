from django.urls import path
from allauth.account.views import LoginView, SignupView

from . import views
from .forms import CustomLoginForm, CustomSignupForm


app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(form_class=CustomSignupForm), name='signup'),
    path('login/', LoginView.as_view(form_class=CustomLoginForm), name='login'),
    path('verify_phone', views.verify_phone, name='verify_phone'),
    path('resend_code', views.resend_code, name='resend_code'),
]

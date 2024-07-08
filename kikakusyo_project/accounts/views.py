from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

class RegistUserView(CreateView):
    template_name = 'us_regist.html'
    form_class = RegistForm

# class UserLoginView(FormView):
#     template_name = 'us_login.html'
#     form_class = UserLoginForm
    
#     def post(self, request, *args, **kwargs):
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(email=email, password=password)
#         if user is not None and user.is_active:
#             login(request, user)
#         return redirect('accounts:home')
class UserLoginView(LoginView):
    template_name = 'us_login.html'
    authentication_form = UserLoginForm
    
    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1200000)
        return super().form_valid(form)


class UserLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:us_login')


class HotelResearchView(CreateView):
    template_name = 'hotel_research.html'

class CyumonInfoView(CreateView):
    template_name = 'cyumon_info.html'

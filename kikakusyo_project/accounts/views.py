from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import View
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Create your views here.


class HomeView(TemplateView):
    template_name = 'home.html'

class RegistUserView(CreateView):
    template_name = 'us_regist.html'
    form_class = RegistForm
    success_url = '/accounts/us_login/'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        messages.success(self.request, "ユーザー登録に成功しました")
        return redirect(self.success_url)
        # return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)
        # return self.render_to_response(self.get_context_data(form=form))

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
        remember = form.cleaned_data.get('remember')
        if remember:
            self.request.session.set_expiry(1200000)
        return super().form_valid(form)
    
    def us_login(request):
        userlogin_form = UserLoginForm(request.POST or None)
        if userlogin_form.is_valid():
            username = userlogin_form.cleaned_data.get('username')
            password = userlogin_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('account:home')
            else:
                return HttpResponse('アカウントがアクティブでないです')
        else:
            return HttpResponse('ユーザーが存在しません')
  

class UserLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:us_login')


class HotelResearchView(CreateView):
    template_name = 'hotel_research.html'

class CyumonInfoView(CreateView):
    template_name = 'cyumon_info.html'

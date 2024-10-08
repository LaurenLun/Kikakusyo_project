from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import FormView
from .forms import RegistForm, UserLoginForm, UserInfoForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import View
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth import update_session_auth_hash, get_user

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

class RegistUserView(CreateView):
    template_name = 'us_regist.html'
    form_class = RegistForm
    success_url = '/accounts/us_login/'
    
    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.save()
            messages.success(self.request, "ユーザー登録に成功しました")
            return redirect(self.success_url)
        except Exception as e:
            print(e)
            return render(self.request, 'error_page.html', {'error': str(e)})
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

class UserInfoView(LoginRequiredMixin, FormView):
    template_name = 'us_info.html'
    form_class = UserInfoForm
    success_url = reverse_lazy('accounts:us_info')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs['initial'] = {
            'last_name' : self.request.user.last_name,
            'first_name' : self.request.user.first_name,
            'zip_code' : self.request.user.zip_code,
            'address' : self.request.user.address,
            'phone_number' : self.request.user.phone_number,
            'email' : self.request.user.email,
        }
        return kwargs
    
    def form_valid(self, form):
        form.update(user=self.request.user)
        messages.success(self.request, "ユーザー情報を更新しました")
        return super().form_valid(form)

# class EmailUpdateView(LoginRequiredMixin, UpdateView):
#     model = User
#     form_class = EmailUpdateForm
#     template_name = 'email_update.html'
#     success_url = reverse_lazy('accounts:us_info')

#     def get_object(self, queryset=None):
#         return self.request.user

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         messages.success(self.request, "メールアドレスを更新しました")
#         return response


class UpdateUserInfoView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserInfoForm
    template_name = 'update_us_info.html'
    success_url = reverse_lazy('accounts:us_info')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # form.update(user=self.request.user)
        user = form.save(commit=False)
        password_changed = False
        if form.cleaned_data['password']:
            print("Password is being changed")
            user.set_password(form.cleaned_data['password'])
            password_changed = True
        user.save()
        
        if password_changed:
            print("Updating session auth hash")
            update_session_auth_hash(self.request, user)
        
        # from django.contrib.auth import get_user
        current_user = get_user(self.request)
        print(f"Is user authenticated after password change: {current_user.is_authenticated}")
    
        messages.success(self.request, 'ユーザー情報が更新されました。')
        return HttpResponseRedirect(reverse('accounts:us_info'))
        # return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field != '__all__': 
                    messages.error(self.request, f"{form.fields[field].label}: {error}")
                else:
                    messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(form=form))
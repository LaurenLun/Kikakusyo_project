from django import forms
from .models import Users
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError  #要屏蔽?
from django.contrib.auth.forms import AuthenticationForm


class RegistForm(forms.ModelForm):
    last_name = forms.CharField(label='名前(姓)')
    first_name = forms.CharField(label='名前(名)')
    zip_code = forms.CharField(label='郵便番号')
    address = forms.CharField(label='住所')
    phone_number = forms.IntegerField(label='電話番号', min_value=0)
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='確認用パスワード', widget=forms.PasswordInput())
    
    class Meta:
        model = Users
        fields = ['last_name', 'first_name', 'zip_code', 'address', 
                  'phone_number', 'email', 'password', 'confirm_password']
        
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("パスワードが一致しません")
        
        return cleaned_data


# class UserLoginForm(forms.Form):
#     email = forms.EmailField(label='メールアドレス')
#     password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)
    
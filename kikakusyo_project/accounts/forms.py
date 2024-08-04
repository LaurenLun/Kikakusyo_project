from django import forms
from django.contrib.auth.models import User
from .models import Users #SampleModel
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError 
import re
from django.contrib.auth.forms import AuthenticationForm

def validate_phone_number(value):
    pattern = r'^(\d{3}-\d{4}-\d{4}|\d{11})$'
    if not re.match(pattern, value):
        raise ValidationError('電話番号は090-1234-5678の形式、もしくは数字11桁で入力してください。')

def validate_zip_code(value):
    pattern = r'^(\d{3}-\d{4}|\d{7})$'
    if not re.match(pattern, value):
        raise ValidationError('郵便番号は123-4567の形式、もしくは数字7桁で入力してください。')
    

class RegistForm(forms.ModelForm):
    last_name = forms.CharField(label='名前(姓)', max_length=10)
    first_name = forms.CharField(label='名前(名)', max_length=10)
    zip_code = forms.CharField(label='郵便番号', max_length=8)
    address = forms.CharField(label='住所', max_length=30)
    phone_number = forms.CharField(label='電話番号', max_length=13)
    email = forms.EmailField(label='メールアドレス', required=True)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='確認用パスワード', widget=forms.PasswordInput())
    
    class Meta:
        model = Users
        fields = ('last_name', 'first_name', 'zip_code', 'address', 
                  'phone_number', 'email', 'password', 'confirm_password')
        labels = {
            'last_name': '名前(姓)', 
            'first_name': '名前(名)', 
            'zip_code': '郵便番号', 
            'address': '住所', 
            'phone_number': '電話番号', 
            'email': 'メールアドレス',
            'password': 'パスワード', 
            'confirm_password': '確認用パスワード',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].validators.append(validate_phone_number)
        self.fields['zip_code'].validators.append(validate_zip_code)
        
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")        
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("パスワードが一致しません")
        
        if password:
            try:
                validate_password(password, self)
            except ValidationError as e:
                self.add_error('password', e)
            
                # raise ValidationError(e.message)
                # return user
                # validate_password(password)
        
        return cleaned_data    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')        
        user.set_password(password)
        if commit:
            user.save()
        return user
        
# class UserLoginForm(forms.Form):
#     email = forms.EmailField(label='メールアドレス')
#     password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス', max_length=150)
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)

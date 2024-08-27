from django import forms
from .models import Users
from django.contrib.auth.models import User
from .models import Users #SampleModel
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError 
import re
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm

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
   

User = get_user_model() 



class UserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = (
            'last_name', 
            'first_name', 
            'zip_code', 
            'address', 
            'phone_number', 
            'email',
            # 'password',
            # 'confirm_password',
        )
        labels = {
            'last_name': '名前(姓)', 
            'first_name': '名前(名)', 
            'zip_code': '郵便番号', 
            'address': '住所', 
            'phone_number': '電話番号', 
            'email': 'メールアドレス',
            # 'password': 'パスワード', 
            # 'confirm_password': '確認用パスワード',
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 設置必填欄位
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['zip_code'].required = True
        self.fields['address'].required = True
        self.fields['phone_number'].required = True
        self.fields['email'].required = True
        # self.fields['password'].required = True
        # self.fields['confirm_password'].required = True
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # self.fields['email'].widget.attrs['placeholder'] = '変更する場合のみ入力してください'
        self.fields['password'].widget.attrs['placeholder'] = '変更する場合のみ入力してください'
        self.fields['confirm_password'].widget.attrs['placeholder'] = '変更する場合のみ入力してください'

        
        # ユーザーの更新前情報をフォームに挿入
        # self.fields['last_name'].widget.attrs['value'] = kwargs.get('initial', {}).get('last_name', '')
        # self.fields['first_name'].widget.attrs['value'] = kwargs.get('initial', {}).get('first_name', '')
        # self.fields['zip_code'].widget.attrs['value'] = kwargs.get('initial', {}).get('zip_code', '')
        # self.fields['address'].widget.attrs['value'] = kwargs.get('initial', {}).get('address', '')
        # self.fields['phone_number'].widget.attrs['value'] = kwargs.get('initial', {}).get('phone_number', '')
        # self.fields['email'].widget.attrs['value'] = kwargs.get('initial', {}).get('email', '')
    
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password
    
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', 'このメールアドレスは既に使用されています。')

        if password and not confirm_password:
            # self.add_error('confirm_password', 'パスワードを確認してください。')
            raise ValidationError("確認用パスワードを入力してください。")
        elif password and password != confirm_password:
            # self.add_error('confirm_password', 'パスワードが一致しません。')
            raise ValidationError("パスワードと確認用パスワードが一致しません。")

        return cleaned_data
    
    
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            pattern = r'^(\d{3}-\d{4}|\d{7})$'
            if not re.match(pattern, zip_code):
                raise ValidationError('郵便番号は123-4567の形式、もしくは数字7桁で入力してください。')
        return zip_code

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            pattern = r'^(\d{3}-\d{4}-\d{4}|\d{11})$'
            if not re.match(pattern, phone_number):
                raise ValidationError('電話番号は090-1234-5678の形式、もしくは数字11桁で入力してください。')
        return phone_number
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['email']:
            user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
        
    def update(self, user):
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        user.zip_code = self.cleaned_data['zip_code']
        user.address = self.cleaned_data['address']
        user.phone_number = self.cleaned_data['phone_number']
        # user.email = self.cleaned_data['email']
        user.save()

# class EmailUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('email',)
#         labels = {'email': 'メールアドレス'}

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['email'].widget.attrs['class'] = 'form-control'

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
#             raise forms.ValidationError('このメールアドレスは既に使用されています。')
#         return email

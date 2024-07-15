from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.urls import reverse_lazy
from django.core.validators import RegexValidator
# Create your models here.


# class SampleModel(models.Model):
#     phone_number_regex = RegexValidator(
#         regex=r'^(\d{3}-\d{4}-\d{4}|\d{11})$', 
#         message="電話番号は'090-1234-5678'の形式、もしくは数字11桁で入力してください。"
#     ) 
#     phone_number = models.CharField(validators=[phone_number_regex], max_length=13, verbose_name='電話番号')
    
#     zip_code_regex = RegexValidator(
#         regex=r'^(\d{3}-\d{4}|\d{7})$', 
#         message="郵便番号は'123-4567'の形式、もしくは数字7桁で入力してください。"
#     )
#     zip_code = models.CharField(validators=[zip_code_regex], max_length=8, verbose_name='郵便番号')

#     print(f"vars is {vars}")

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username = username,
            email = email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None):
        user = self.model(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()
    
    def get_absolute_url(self):
        return reverse_lazy('accounts:home')    
from django.urls import path
from .views import(
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, UserInfoView,  UpdateUserInfoView,
    )

app_name = 'accounts'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('us_regist/', RegistUserView.as_view(), name='us_regist'),
    path('us_login/', UserLoginView.as_view(), name='us_login'),
    path('us_logout/', UserLogoutView.as_view(), name='us_logout'),
    path('us_info/', UserInfoView.as_view(), name='us_info'),
    path('update_us_info/', UpdateUserInfoView.as_view(), name='update_us_info'),
    # path('update_email/', EmailUpdateView.as_view(), name='update_email'),
]



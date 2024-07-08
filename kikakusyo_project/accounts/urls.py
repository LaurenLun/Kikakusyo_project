from django.urls import path
from .views import(
    RegistUserView, HomeView, UserLoginView,
    UserLogoutView, HotelResearchView, CyumonInfoView,
)

app_name = 'accounts'
urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('us_regist/', RegistUserView.as_view(), name='us_regist'),
    path('us_login/', UserLoginView.as_view(), name='us_login'),
    path('us_logout/', UserLogoutView.as_view(), name='us_logout'),
    path('hotel_research/', HotelResearchView.as_view(), name='hotel_research'),
    path('cyumon_info/', CyumonInfoView.as_view(), name='cyumon_info'),

]


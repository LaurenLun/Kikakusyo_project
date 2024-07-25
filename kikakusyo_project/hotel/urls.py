from django.urls import path
from .views import(
    HotelListView, HotelSearchView, CyumonInfoView, PlanListView,
)

app_name = 'hotel'
urlpatterns = [
    path('hotel-search/', HotelSearchView.as_view(), name='hotel_search'),
    path('hotel_list/', HotelListView.as_view(), name='hotel_list'),
    path('plan_list/<int:pk>/', PlanListView.as_view(), name='plan_list'),
    path('cyumon_info/', CyumonInfoView.as_view(), name='cyumon_info'),
]

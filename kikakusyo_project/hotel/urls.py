from django.urls import path
from .views import(
    HotelListView, HotelSearchView, CyumonInfoView, PlanListView, 
    PlanListCalendarView, add_product, CyumonInfoUpdateView, 
    CyumonInfoDeleteView, InputUserAddressesView, ConfirmOrderView, OrderSuccessView,
)
# from . import views

app_name = 'hotel'
urlpatterns = [
    path('hotel-search/', HotelSearchView.as_view(), name='hotel_search'),
    path('hotel_list/', HotelListView.as_view(), name='hotel_list'),
    path('plan_list/<int:pk>/', PlanListView.as_view(), name='plan_list'),
    path('plan_list/<int:pk>/calendar/', PlanListCalendarView.as_view(), name='calendar'),
    path('plan_list/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', PlanListCalendarView.as_view(), name='calendar'),
    path('cyumon_info/', CyumonInfoView.as_view(), name='cyumon_info'),
    path('cyumon_info/<int:hotel_id>/', CyumonInfoView.as_view(), name='cyumon_info'),
    path('add_product/', add_product, name='add_product'),
    path('cyumoninfo_update/<int:pk>/', CyumonInfoUpdateView.as_view(), name='cyumoninfo_update'),
    path('cyumoninfo_delete/<int:pk>/', CyumonInfoDeleteView.as_view(), name='cyumoninfo_delete'),
    path('input_useraddresses/', InputUserAddressesView.as_view(), name='input_useraddresses'),
    path('input_useraddresses/<int:pk>/', InputUserAddressesView.as_view(), name='input_useraddresses_update'),
    path('confirm_order/', ConfirmOrderView.as_view(), name='confirm_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
]

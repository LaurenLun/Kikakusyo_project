from django.urls import path
from .views import(
    HotelListView, HotelSearchView, CyumonInfoView, PlanListView, 
    PlanListCalendarView, add_product, CyumonInfoUpdateView, apply_kupon,
    CyumonInfoDeleteView, InputUserAddressesView, ConfirmOrderView, OrderSuccessView,
    DeleteUserAddressView, OrdersDetailView, OrdersListView, DeleteOrderView, some_error_page,
    # room_list, reservation_confirm, 
    cancel_reservation, update_quantity, delete_item,
)
# from . import views

app_name = 'hotel'
urlpatterns = [
    path('hotel-search/', HotelSearchView.as_view(), name='hotel_search'),
    path('hotel_list/', HotelListView.as_view(), name='hotel_list'),
    path('plan_list/<int:hotel_id>/', PlanListView.as_view(), name='plan_list'),
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
    path('apply-kupon/', apply_kupon, name='apply_kupon'),
    path('delete_useraddress/<int:pk>/', DeleteUserAddressView.as_view(), name='delete_useraddress'),
    path('order_success_list/', OrdersListView.as_view(), name='order_success_list'),
    path('order_success_info/<int:pk>/', OrdersDetailView.as_view(), name='order_success_info'),
    # path('delete_order/<int:pk>/', DeleteOrderView.as_view(), name='delete_order'),
    path('error/', some_error_page, name='some_error_page'),
    path('order/<int:pk>/delete/', DeleteOrderView.as_view(), name='delete_order'),
    path('order/<int:order_id>/cancel/', cancel_reservation, name='cancel_reservation'),
    path('update_quantity/', update_quantity, name='update_quantity'),
    path('delete_item/', delete_item, name='delete_item'),
]

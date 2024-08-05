from django.shortcuts import render, get_object_or_404, redirect
from .models import(
    HotelName, PlanName, HotelPictures, CyumonInfo, PlanListCalendar, 
    Carts, CartItems, UserAddresses, Orders, OrderItems,
)
from .forms import(
    CyumonInfoUpdateForm, UserAddressesInputForm,
)
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView,
)
from django.urls import reverse_lazy
# from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
import os
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, date, timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.db import transaction
from django.forms.models import model_to_dict
from django.contrib import messages
# from .forms import HotelForm
# Create your views here.

def hotel_search(request):
    hotels = HotelName.objects.all()
    return render(request, 'hotel_search.html', {'hotels': hotels})

def plan_list_view(request):
    plans = PlanName.objects.all()
    return render(request, 'hotel/plan_list.html', {'plans': plans})


class HotelSearchView(ListView):
    model = HotelName
    template_name = 'hotel/hotel_search.html'
    context_object_name = 'hotels'
    
    def get_queryset(self):
        return HotelName.objects.all().order_by('name')
    
class HotelListView(LoginRequiredMixin, ListView):
    model = HotelName
    template_name = os.path.join('hotel/hotel_list.html')
    context_object_name = 'hotels'
    
class PlanListView(ListView):
    model = PlanName
    template_name = os.path.join('hotel/plan_list.html')
    context_object_name = 'plans'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'ログインしてから予約注文に進んでください')
            return redirect('accounts:us_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hotel'] = self.hotel
        context['pictures'] = PlanName.objects.filter(hotel=self.hotel).order_by('order')
        context['room_type'] = self.room_type
        context['descending'] = self.request.GET.get('order_by_price') == '1'
        context['ascending'] = self.request.GET.get('order_by_price') == '2'
        context['checkin_date'] = self.request.GET.get('checkin', '')
        context['checkout_date'] = self.request.GET.get('checkout', '')
        
        cart, _ = Carts.objects.get_or_create(user=self.request.user)
        
        if self.object_list.exists():
            product_id = self.object_list.first().id
            context['is_added'] = CartItems.objects.filter(
                cart_id=self.request.user.id,
                # cart=cart,
                product_id=product_id
            ).exists()
        else:
            context['is_added'] = False

        return context

    def get_queryset(self):
        self.hotel = get_object_or_404(HotelName, pk=self.kwargs['pk'])
        query = PlanName.objects.filter(hotel=self.hotel).prefetch_related('pictures')
        
        self.room_type = self.request.GET.get('room_type', '')
        if self.room_type and self.room_type != '全部屋タイプ':
            query = query.filter(room_type=self.room_type)
            
        checkin_date = self.request.GET.get('checkin')
        checkout_date = self.request.GET.get('checkout')
        
        if checkin_date and checkout_date:
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()
            query = query.filter(
                Q(checkin__lte=checkout_date) & Q(checkout__gte=checkin_date)
            )
        
        # for plan in query:
        #     logger.debug(f"Plan: {plan.name}, Pictures: {list(plan.pictures.all())}")
        # return super().get_queryset().filter(hotel=self.hotel)
        order_by_price = self.request.GET.get('order_by_price', '')
        if order_by_price == '1':
            query = query.order_by('price')
        elif order_by_price == '2':
            query = query.order_by('-price')
        
        logger.debug(f"room_type: {self.room_type}, order_by_price: {order_by_price}")
        logger.debug(f"Query: {query.query}")
        logger.debug(f"Number of results: {query.count()}")
        
        
        return query
    
         
class CyumonInfoView(LoginRequiredMixin, TemplateView):
    model = CyumonInfo
    template_name = os.path.join('hotel', 'cyumon_info.html')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # if not self.request.user.is_authenticated:
        #     messages.info(self.request, 'ログインしてから予約注文に進んでください')
        #     # context['login_required'] = True
        #     return redirect('accounts:us_login')
               
        user_id = self.request.user.id
        hotel_id = self.kwargs.get('hotel_id')
        query = CartItems.objects.filter(cart_id=user_id)
        total_price = 0
        items = []
        for item in query.all():
            total_price += item.quantity * item.product.price
            picture = item.product.pictures.first()
            picture_url = picture.image.url if picture else None
            in_stock = True if item.product.stock >= item.quantity else False
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture_url,
                'id': item.id,
                'name': item.product.name,
                'price': item.product.price,
                'in_stock': in_stock,
                'hotel_name': item.product.hotel.name if item.product.hotel else 'Unknown Hotel',
                'checkin': item.product.checkin,
                'checkout': item.product.checkout,
            }
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        context['plans'] = PlanName.objects.filter(hotel=hotel_id)
        return context

    def get_queryset(self):
        return CyumonInfo.objects.all()
    

class PlanListCalendarView(generic.TemplateView):
    template_name = 'hotel/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = get_object_or_404(PlanName, pk=self.kwargs['pk'])
        today = date.today()
        
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            base_date = datetime.date(year=year, month=month, day=day)
        else:
            base_date = today
        
        days = [base_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]
        
        start_time = datetime.combine(start_day, datetime.min.time())
        end_time = datetime.combine(end_day, datetime.max.time())
        
        plan_bookings = PlanListCalendar.objects.filter(plans=plans).exclude(start__gt=end_time).exclude(end__lt=start_time)
        
        calendar_data = {}
        for booking in plan_bookings:
            local_dt = timezone.localtime(booking.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_date not in calendar_data:
                calendar_data[booking_date] = {}
            calendar_data[booking_date][booking_hour] = False

        context['plans'] = plans
        context['calendar'] = calendar_data
        context['days'] = days
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['before'] = days[0] - timedelta(days=7)
        context['next'] = days[-1] + timedelta(days=1)
        context['today'] = today
        context['public_holidays'] = settings.PUBLIC_HOLIDAYS
        context['checkin'] = plans.checkin
        context['checkout'] = plans.checkout
        return context

@login_required
def add_product(request):
    logger.debug(f"Received request: {request.POST}")
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'ログインしてから予約注文に進んでください', 'redirect': reverse('accounts:us_login')}, status=401)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        
        if not quantity:
            return JsonResponse({'message': '数量は空にできません'}, status=400)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return JsonResponse({'message': '0以上の値を入力してください'}, status=400)
            
            product = get_object_or_404(PlanName, id=product_id)
            if quantity > product.stock:
                return JsonResponse({'message': '部屋数を超えています'}, status=400)
            
            cart, _ = Carts.objects.get_or_create(user=request.user)
            cart_item, created = CartItems.objects.get_or_create(product=product, cart=cart)

            if not created:
                return JsonResponse({'message': 'このプランは既に予約注文に追加されています'}, status=400)
            
            cart_item.quantity = quantity
            cart_item.save()
            
            cart_count = cart.cartitems_set.count()
            return JsonResponse({'message': '希望するプランを予約注文に追加しました', 'cart_count': cart_count})
              
        except ValueError:
            return JsonResponse({'message': '無効の数値です'}, status=400)
        
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")
            return JsonResponse({'message': str(e)}, status=400)
    
    if not created:
        if cart_item.quantity + quantity > product.stock:
            return JsonResponse({'message': '部屋数を超えています'}, status=400)
        cart_item.quantity += quantity
        cart_item.save()
        return JsonResponse({'message': 'プランの数量を更新しました'})
        
    return JsonResponse({'message': '無効なリクエストです'}, status=400)


class CyumonInfoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('hotel', 'cyumoninfo_update.html')
    form_class = CyumonInfoUpdateForm
    model = CartItems
    success_url = reverse_lazy('hotel:cyumon_info')

class CyumonInfoDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('hotel', 'cyumoninfo_delete.html')
    model = CartItems
    success_url = reverse_lazy('hotel:cyumon_info')

class InputUserAddressesView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('hotel', 'input_useraddresses.html')
    form_class = UserAddressesInputForm
    # success_url = reverse_lazy('hotel:confirm_order')
    model = UserAddresses
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(UserAddresses, pk=pk, user=self.request.user)
        return None
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        cart, created = Carts.objects.get_or_create(user=self.request.user)
        if not cart.cartitems_set.all():
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
        
        self.object = None
        # pk = kwargs.get('pk')
        # cart, created = Carts.objects.get_or_create(user=self.request.user)
        return super().get(request, *args, **kwargs)
        
        # if pk:
        #     self.object = get_object_or_404(UserAddresses, pk=pk, user=self.request.user)
        #     form = self.get_form()
        #     form.initial = model_to_dict(self.object)
        # else:
        #     form = self.get_form()
        
        # return self.render_to_response(self.get_context_data(form=form))
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        # return reverse('hotel:confirm_order')
        
        # cache.set(f'address_user_{self.request.user.id}', form.instance, timeout=None)
        
        kupon_amount = self.request.GET.get('kupon_amount', 0)
        return f"{reverse('hotel:confirm_order')}?address_id={self.object.id}&kupon_amount={kupon_amount}"
        # url += f'?address_id={form.instance.id}&kupon_amount={kupon_amount}'
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kupon_amount'] = self.request.GET.get('kupon_amount', 0)
        address = cache.get(f'address_user_{self.request.user.id}')
        pk = self.kwargs.get('pk')
        address = get_object_or_404(UserAddresses, user_id=self.request.user.id, pk=pk) if pk else address
        if address:
            context['form'].fields['last_name'].initial = address.last_name
            context['form'].fields['first_name'].initial = address.first_name
            context['form'].fields['zip_code'].initial = address.zip_code
            context['form'].fields['address'].initial = address.address
            context['form'].fields['phone_number'].initial = address.phone_number
        
        else:
            address = cache.get(f'address_user_{self.request.user.id}')
            if address:
                context['form'].initial = model_to_dict(address)
        
        context['useraddresses'] = UserAddresses.objects.filter(user=self.request.user).all()
        return context
    

class ConfirmOrderView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('hotel', 'confirm_order.html')
    
    # def insert_cart(self, cart, useraddresses, total_price):
    #     return created_order
    
    def safe_float(value, default=0.0):
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
        
        
    def get(self, request, *args, **kwargs):
        # context = self.get_context_data(**kwargs)
        # return self.render_to_response(context)
        # useraddresses = context.get('useraddresses')
        
        cart, created = Carts.objects.get_or_create(user=self.request.user)
        if not cart.cartitems_set.exists():
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
       
        address_id = self.request.GET.get('address_id')
        
        if address_id:
            useraddresses = get_object_or_404(UserAddresses, id=address_id, user=self.request.user)
        else:
            useraddresses = cache.get(f'address_user_{self.request.user.id}')
        if not useraddresses:
            # messages.error(request, '住所情報が見つかりません')
            return redirect('hotel:input_useraddresses')
        
        context = self.get_context_data(useraddresses=useraddresses)
        return self.render_to_response(context)
    
        # if context.get('cart_empty'):
        #     messages.error(request, '購物車に商品がありません')
        #     return redirect('hotel:cyumon_info')
    
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Carts.objects.filter(user=self.request.user).first()
        useraddresses = kwargs.get('useraddresses')
        # address_id = self.request.GET.get('address_id')
        if not cart:
            logger.warning(f"No cart found for user {self.request.user}")
            return context
        
        # if address_id:
        #     useraddresses = get_object_or_404(UserAddresses, id=address_id, user=self.request.user)
        # else:
        #     useraddresses = cache.get(f'address_user_{self.request.user.id}')
        # if not useraddresses:
        #     return context
            
        # print(f"Debug: useraddresses = {useraddresses}")
        context['cart'] = cart
        context['useraddresses'] = UserAddresses.objects.filter(user=self.request.user).first()
        context['kupon_amount'] = self.request.GET.get('kupon_amount', 0)
        context['total_price'] = sum(item.product.price * item.quantity for item in cart.cartitems_set.all())
       
        # cart, created = Carts.objects.get_or_create(user=self.request.user)
        
        # if not cart.cartitems_set.exists():
        #     messages.error(request, '購物車に商品がありません')
        #     return redirect('hotel:cyumon_info')
        if cart:
            context['cart'] = cart 
        else:
            context['cart'] = None
            context['total_price'] = 0
            context['items'] = []
        
        # if not cart.cartitems_set.exists():
        #     context['cart_empty'] = True
        #     return context

        
        total_price = 0
        items = []
        
        for item in cart.cartitems_set.all():
            total_price += item.quantity * item.product.price
            picture = item.product.pictures.first()
            picture = picture.image if picture else None
            item_context = item.get_context_data()
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'price': item.product.price,
                'id': item.id,
                'room_type': item.product.room_type,
                'people': item.product.people,
                'hotel_name': item.product.hotel.name if item.product.hotel else 'Unknown Hotel',
                'checkin': item_context['checkin'],
                'checkout': item_context['checkout'],
            }        
            items.append(tmp_item)
        context['total_price'] = float(total_price)
        context['items'] = items
        
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        logger.info("Starting order confirmation process")
        context = self.get_context_data()
        useraddresses = context.get('useraddresses')
        cart = context.get('cart')
        # if not cart.id:
        #     cart.save()
        
        logger.debug(f"User: {request.user}, Cart: {cart}, Useraddresses: {useraddresses}")
        
        if not cart:
            logger.warning("Cart is empty, redirecting to cyumon_info")
            messages.error(request, '購物車が空です')
            return redirect('hotel:cyumon_info') 
        
        if not cart.cartitems_set.exists():
            logger.warning("No items in cart, redirecting to cyumon_info")
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
        
        
        if not useraddresses:
            messages.error(request, '住所情報が見つかりません')
            return redirect('hotel:input_useraddresses')
            
        total_price = context.get('total_price', 0)
        kupon_amount_str = request.POST.get('kupon_amount', 0)
        
        logger.debug(f"Total price: {total_price}, Kupon amount: {kupon_amount_str}")
        
        if total_price <= 0:
            logger.warning("Invalid total price, redirecting to cyumon_info")
            messages.error(request, '合計金額が無効です')
            return redirect('hotel:cyumon_info')
        
        try: 
            kupon_amount = int(kupon_amount_str) if kupon_amount_str else 0
            actual_total_price = float(total_price or 0) - kupon_amount
            
            request.session['order_info'] = {
                'cart_id': str(cart.user_id),
                'total_price': float(actual_total_price),
                'kupon_amount': kupon_amount,
            }
            
            if (not useraddresses) or (not cart) or (not total_price):
                raise Http404('予約注文を処理でエラーが発生しました')
            
            for item in cart.cartitems_set.all():
                if item.quantity > item.product.stock:
                    raise Http404('予約注文処理でエラーが発生しました')

            
            order = Orders.objects.insert_cart(cart, useraddresses, actual_total_price)
            OrderItems.objects.insert_cart_items(cart, order)
            PlanName.objects.reduce_stock(cart)
            
            logger.info(f"Order created successfully: {order.id}")
            request.session['completed_order_id'] = order.id
            cart.delete()
            logger.info("Redirecting to order success page")
            return redirect('hotel:order_success')
        
        
            # cart.delete()            
            # return response
        
        # except ValueError:
        #     kupon_amount = 0
        #     messages.error(request, 'クーポン額が無効です')
        
        # except Http404 as e:
        #     messages.error(request, str(e))
        
        except Exception as e:
            logger.error(f"Error during order processing: {str(e)}")
            messages.error(request, f'予約注文処理で予期せぬエラー発生しました: {str(e)}')
            
            # return redirect('hotel:confirm_order')
    
            return render(request, 'hotel/order_success.html', {'order': order})
    
                    
        # if (not useraddresses) or (not cart) or (not total_price):
        #     raise Http404('予約注文を処理でエラーが発生しました')
        # for item in cart.cartitems_set.all():
        #     if item.quantity > item.product.stock:
        #         raise Http404('予約注文処理でエラーが発生しました')
        # order = Orders.objects.insert_cart(cart, useraddresses, total_price - kupon_amount)
        # OrderItems.objects.insert_cart_items(cart, order)
        # PlanName.objects.reduce_stock(cart)
        # cart.delete()
        # return redirect(reverse_lazy('hotel:order_success'))


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    
    template_name = os.path.join('hotel', 'order_success.html')
    
    def get(self, request, *args, **kwargs):
        logger.info("Accessing OrderSuccessView")
        order_id = request.session.get('completed_order_id')
        logger.debug(f"Completed order ID from session: {order_id}")
        
        if not order_id:
            logger.warning("No completed order ID in session")
            messages.error(request, '有効な注文が見つかりません')
            return redirect('hotel:cyumon_info')
        
        try:
            order = Orders.objects.get(id=order_id, user=request.user)
            logger.info(f"Found order: {order.id}")
            del request.session['completed_order_id']
            # context = self.get_context_data(order=order)
            return self.render_to_response(self.get_context_data(order=order))
            
        except Orders.DoesNotExist:
            logger.error(f"Order with ID {order_id} not found for user {request.user}")
            messages.error(request, '注文が見つかりません')
            return redirect('hotel:cyumon_info')
        
        # # 清除會話中的訂單ID
        # del request.session['completed_order_id']  
        
        # context = self.get_context_data(order=order)
        # return self.render_to_response(context)
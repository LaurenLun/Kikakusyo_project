from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from .models import(
    HotelName, PlanName, HotelPictures, CyumonInfo, PlanListCalendar, 
    Carts, CartItems, UserAddresses, Orders, OrderItems,
)
from .forms import(
    CyumonInfoUpdateForm, UserAddressesInputForm,
)
from django.views.generic.list import ListView
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import (
    UpdateView, DeleteView, CreateView, DeleteView,
)
from django.urls import reverse_lazy
# from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import array
is_addedList = array.array("h", [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
from datetime import datetime, date, timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.db import transaction
from django.forms.models import model_to_dict
from django.contrib import messages
from datetime import datetime
# from .forms import HotelForm
# Create your views here.

def hotel_search(request):
    hotels = HotelName.objects.all()
    return render(request, 'hotel_search.html', {'hotels': hotels})

def plan_list_view(request):
    plans = PlanName.objects.all()
    return render(request, 'hotel/plan_list.html', {'plans': plans})

@require_POST
def apply_kupon(request):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponseBadRequest("Only AJAX requests are allowed")
    
    kupon_amount = int(request.POST.get('kupon_amount', 0))
    cart = Carts.objects.filter(user=request.user).first()
    total_price = sum(item.product.price * item.quantity * ((item.checkout - item.checkin).days if item.checkin and item.checkout else 1) for item in cart.cartitems_set.all())
    discounted_price = max(0, total_price - kupon_amount)
    # new_total = calculate_new_total(kupon_amount) 
    
    return JsonResponse({
        'total_price': total_price,
        'discounted_price': discounted_price,
        'kupon_amount': kupon_amount
    })

def calculate_new_total(kupon_amount):
    # 實現計算新總額的邏輯
    # 這裡只是一個示例，您需要根據實際情況來計算
    cart_total = 10000  # 假設購物車總額是 10000
    return max(0, cart_total - kupon_amount)

@login_required
def input_address_view(request):
    user = request.user
    context = {
        'last_name': user.last_name,
        'first_name': user.first_name,
        'zip_code': user.zip_code,
        'address': user.address,
        'phone_number': user.phone_number,
    }
    return render(request, 'hotel/input_useraddresses.html', context)



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
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        # hotel_id = self.kwargs.get('hotel_id')
        # plan = {
        #     "id": list(range(1, 17))
        # }
        # context['plan'] = plan
        # context['is_addedList_ForHtml'] = {id: 0 for id in plan['id']}
        # context['hotel_id'] = hotel_id
        return self.render_to_response(context)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'ログインしてから予約注文に進んでください')
            return redirect('accounts:us_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel_id = self.kwargs.get('hotel_id')
        context['hotel'] =  get_object_or_404(HotelName, id=hotel_id)
        context['pictures'] = PlanName.objects.filter(hotel=context['hotel']).order_by('order')
        context['room_type'] = self.room_type
        context['descending'] = self.request.GET.get('order_by_price') == '1'
        context['ascending'] = self.request.GET.get('order_by_price') == '2'
        # context['checkin_date'] = self.request.GET.get('checkin', '')
        # context['checkout_date'] = self.request.GET.get('checkout', '')
        
        cart, _ = Carts.objects.get_or_create(user=self.request.user)
        
        # 124~133 小李
        if 'cartitems' not in context:
            context['cartitems'] = []
        for i in range(1, 16):
            if CartItems.objects.filter(
                cart_id=self.request.user.id,
                product_id=i
            ).exists():
                context['cartitems'].append(i)
            elif i in context['cartitems']:
                context['cartitems'].remove(i)
        
        # 136~140 香港同事
        # for i in range(1, 16):
        #     context['is_added_test'+ str(i)] = CartItems.objects.filter(
        #         cart_id=self.request.user.id,
        #         product_id=i
        #     ).exists()
        
        
        
        #這邊140~158先保留  
        # plan_ids = list(range(1, 17))
        # context['plan'] = {"id": plan_ids}
        # context['is_addedList_ForHtml'] = {
        #     id: CartItems.objects.filter(cart__user=self.request.user, product_id=id).exists()
        #     for id in plan_ids
        # }
                
        # if self.object_list.exists():
        #     product_id = self.object_list.first().id
        #     temp_idx = 0
        #     context['is_added'+ str(temp_idx)] = False
        #     context['cart_product_id'] = product_id 
        #     context['is_added'] = CartItems.objects.filter(
        #         cart_id=self.request.user.id,
        #         # cart=cart,
        #         product_id=product_id,       
        #     ).exists()
        # else:
        #     context['is_added'] = False

        return context

    def get_queryset(self):
        self.hotel = get_object_or_404(HotelName, pk=self.kwargs['hotel_id'])
        query = PlanName.objects.filter(hotel=self.hotel).prefetch_related('pictures')
        
        self.room_type = self.request.GET.get('room_type', '')
        if self.room_type and self.room_type != '全部屋タイプ':
            query = query.filter(room_type=self.room_type)
            
        # checkin_date = self.request.GET.get('checkin')
        # checkout_date = self.request.GET.get('checkout')
        
        # if checkin_date and checkout_date:
        #     checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        #     checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()
        #     query = query.filter(
        #         Q(checkin__lte=checkout_date) & Q(checkout__gte=checkin_date)
        #     )
        
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
                # 'checkin': item.product.checkin,
                # 'checkout': item.product.checkout,
            }
            items.append(tmp_item)

        context['total_price'] = total_price
        context['items'] = items
        context['plans'] = PlanName.objects.filter(hotel=hotel_id)

        kupon_amount = int(self.request.GET.get('kupon_amount', 0))
        context['kupon_amount'] = kupon_amount
        context['discounted_price'] = context['total_price'] - context['kupon_amount']
        # context['kupon_amount'] = self.request.GET.get('kupon_amount', 0)
        
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
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        
        try:
            checkin = datetime.strptime(checkin, '%Y-%m-%d').date() if checkin else None
            checkout = datetime.strptime(checkout, '%Y-%m-%d').date() if checkout else None
        except ValueError:
            return JsonResponse({'message': '无效的日期格式'}, status=400)
        
        
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
            cart_item, created = CartItems.objects.get_or_create(
                product=product, 
                cart=cart,
                defaults={'quantity': quantity, 'checkin': checkin, 'checkout': checkout}
            )

            if not created:
                return JsonResponse({'message': 'このプランは既に予約注文に追加されています'}, status=400)
            
            cart_item.quantity = quantity
            cart_item.checkin = checkin
            cart_item.checkout = checkout
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
    object= None
    
    
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
        
        self.object = self.get_object()
        form = self.get_form()
        
        if self.object:
            form.initial = model_to_dict(self.object)
        
        else:
            checkin = request.GET.get('checkin')
            checkout = request.GET.get('checkout')
            if checkin and checkout:
                form = self.get_form()
                form.initial['checkin'] = checkin
                form.initial['checkout'] = checkout
        
        
        cart, created = Carts.objects.get_or_create(user=self.request.user)
        if not cart.cartitems_set.all():
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
        
        # self.object = None
        # pk = kwargs.get('pk')
        # cart, created = Carts.objects.get_or_create(user=self.request.user)
        # return super().get(request, *args, **kwargs)
        return self.render_to_response(self.get_context_data(form=form))
        
        # if pk:
        #     self.object = get_object_or_404(UserAddresses, pk=pk, user=self.request.user)
        #     form = self.get_form()
        #     form.initial = model_to_dict(self.object)
        # else:
        #     form = self.get_form()
        
        # return self.render_to_response(self.get_context_data(form=form))
    
    
    def post(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            # address = form.save(commit=False)
            # address.user = request.user
            # address.save()
            # # checkin = request.POST.get('checkin')
            # # checkout = request.POST.get('checkout')
            
            # # if checkin:
            # #     address.checkin = datetime.strptime(checkin, '%Y-%m-%d').date()
            # # if checkout:
            # #     address.checkout = datetime.strptime(checkout, '%Y-%m-%d').date()
        
            # request.session['latest_address_id'] = address.id            
            # cache.set(f'address_user_{request.user.id}', address, timeout=None)
            return self.form_valid(form)
        else:
            logger.warning(f"Form validation failed: {form.errors}")
            return self.form_invalid(form)
        
        # return super().post(request, *args, **kwargs)    
    
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
            context['form'].fields['checkin'].initial = address.checkin
            context['form'].fields['checkout'].initial = address.checkout
            
        
        else:
            address = cache.get(f'address_user_{self.request.user.id}')
            if address:
                context['form'].initial = model_to_dict(address)
        
        context['useraddresses'] = UserAddresses.objects.filter(user=self.request.user).all()
        return context   
    
    
    def form_valid(self, form):
        # form.instance.user = self.request.user
        # response = super().form_valid(form)
        # if self.object:
        #     for field, value in form.cleaned_data.items():
        #         setattr(self.object, field, value)
            
        #     self.object.save()
        
        # else:
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.checkin = form.cleaned_data['checkin']
        self.object.checkout = form.cleaned_data['checkout']
        self.object.save()
        
        self.request.session['selected_address_id'] = self.object.id
        cart = Carts.objects.filter(user=self.request.user).first()
        if cart:
            for item in cart.cartitems_set.all():
                item.checkin = self.object.checkin
                item.checkout = self.object.checkout
                item.save()
        
        
        # self.object = form.save()
        # kupon_amount = self.request.GET.get('kupon_amount', self.request.GET.get('kupon_amount', 0))
        kupon_amount = self.request.GET.get('kupon_amount', 0)
        success_url = f"{reverse('hotel:confirm_order')}?address_id={self.object.id}&kupon_amount={kupon_amount}"
        return HttpResponseRedirect(success_url)
        
        # return super().form_valid(form)
        
        # except Exception as e:
        #     logger.error(f"Error saving UserAddress: {str(e)}")
        #     return self.form_invalid(form)
        # form.instance.user = self.request.user
        # form.instance.checkin = self.request.POST.get('checkin')
        # form.instance.checkout = self.request.POST.get('checkout')
        # return super().form_valid(form)        
    
    def get_success_url(self):
        kupon_amount = self.request.GET.get('kupon_amount', 0)
        return f"{reverse('hotel:confirm_order')}?address_id={self.object.id}&kupon_amount={kupon_amount}"

    
    
    def get_queryset(self):
        self.hotel = get_object_or_404(HotelName, pk=self.kwargs['pk'])
        query = PlanName.objects.filter(hotel=self.hotel).prefetch_related('pictures')
        
        checkin_date = self.request.GET.get('checkin')
        checkout_date = self.request.GET.get('checkout')
            
        if checkin_date and checkout_date:
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()
            query = query.filter(
                Q(checkin__lte=checkout_date) & Q(checkout__gte=checkin_date)
        )
    


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
        # logger.debug(f"Getting address: {address_id} for user: {request.user.id}")
        # cart, created = Carts.objects.get_or_create(user=self.request.user)
        cart = Carts.objects.filter(user=self.request.user).first()
        if not cart or not cart.cartitems_set.exists():
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
       
        address_id = request.GET.get('address_id') 
        kupon_amount = request.GET.get('kupon_amount', 0)
        
        if not address_id:
            messages.error(request, '住所情報が見つかりません')
            return redirect('hotel:input_useraddresses')
        
        try:
            address = UserAddresses.objects.get(id=address_id, user=self.request.user)
        except UserAddresses.DoesNotExist:
            messages.error(request, '住所情報が見つかりません')
            return redirect('hotel:input_useraddresses')
        
        if isinstance(kupon_amount, str):
            try:
                kupon_amount = int(kupon_amount.split('?')[0])
            except ValueError:
                kupon_amount = 0
        elif not isinstance(kupon_amount, int):
            kupon_amount = 0

        if not address_id:
            return redirect('hotel:input_useraddresses')
        
        

        # else:
            # useraddresses = UserAddresses.objects.filter(user=self.request.user).last()
            # return redirect('hotel:input_useraddresses')
        # if not useraddresses:
        #     # messages.error(request, '住所情報が見つかりません')
        #     return redirect('hotel:input_useraddresses')
        
        context = self.get_context_data(address=address, kupon_amount=kupon_amount)
        return self.render_to_response(context)
    
        # if context.get('cart_empty'):
        #     messages.error(request, '購物車に商品がありません')
        #     return redirect('hotel:cyumon_info')
    
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Carts.objects.filter(user=self.request.user).first()
        address = kwargs.get('address')
        
        if not address:
            address_id = self.request.GET.get('address_id')
            if address_id:
                address = UserAddresses.objects.filter(id=address_id, user=self.request.user).first()
            
        if not address:
            address = UserAddresses.objects.filter(user=self.request.user).last()  
        
        kupon_amount = kwargs.get('kupon_amount', 0)
        # address_id = self.request.GET.get('address_id')
        if isinstance(kupon_amount, str):
            try:
                kupon_amount = int(kupon_amount.split('?')[0])  # 取第一個問號前的部分
            except ValueError:
                kupon_amount = 0
        elif not isinstance(kupon_amount, int):
            kupon_amount = 0
            
        if not cart:
            logger.warning(f"No cart found for user {self.request.user}")
            return context
        
        context['cart'] = cart
        # context['address'] = kwargs.get('address')
        context['address'] = address
        # context['address'] = address or UserAddresses.objects.filter(user=self.request.user).first()
        # context['kupon_amount'] = self.request.GET.get('kupon_amount', 0)
        # context['total_price'] = sum(item.product.price * item.quantity for item in cart.cartitems_set.all())
       
        # cart, created = Carts.objects.get_or_create(user=self.request.user)
        
        # if not cart.cartitems_set.exists():
        #     messages.error(request, '購物車に商品がありません')
        #     return redirect('hotel:cyumon_info')
        
        
        total_price = sum(item.quantity * item.product.price for item in cart.cartitems_set.all())
        
        # context['total_price'] = total_price
        # context['kupon_amount'] = kupon_amount
        # context['discounted_price'] = max(0, total_price - int(kupon_amount))
        
        items = []
        total_price = 0
        
        for item in cart.cartitems_set.all():
            # item_price = item.quantity * item.product.price
            # total_price += item_price
        
            picture = item.product.pictures.first()
            item_context = item.get_context_data()
            
            checkin = item_context['checkin']
            checkout = item_context['checkout']
            nights = 0
            
            if checkin and checkout:
                # if isinstance(checkin, str):
                #     checkin = datetime.strptime(checkin, '%Y-%m-%d').date()
                # if isinstance(checkout, str):
                #     checkout = datetime.strptime(checkout, '%Y-%m-%d').date()
                nights = (checkout - checkin).days
            
            item_total = item.product.price * item.quantity * max(nights, 1)
            total_price += item_total
        
            tmp_item = {
                'quantity': item.quantity,
                'picture': item.product.pictures.first().image if item.product.pictures.first() else None,
                'name': item.product.name,
                'price': item.product.price,
                'id': item.id,
                'room_type': item.product.room_type,
                'people': item.product.people,
                'hotel_name': item.product.hotel.name if item.product.hotel else 'Unknown Hotel',
                'checkin': item.checkin,
                'checkout': item.checkout,
                'nights': nights,
                'item_total': item_total,
                # 'kupon_amount': item.kupon_amount,
            }        
            items.append(tmp_item)
            print(f"Item: {tmp_item['name']}, Nights: {nights}, Total: {item_total}")

        context['items'] = items
        context['total_price'] = total_price
        context['kupon_amount'] = int(self.request.GET.get('kupon_amount', 0))
        context['discounted_price'] = max(0, total_price - int(kupon_amount))
        
        # print("Items:", items)
        # print("Total Price:", total_price)
        # print("Kupon Amount:", kupon_amount)
        # print("Discounted Price:", context['discounted_price'])
        print(f"Context items: {context['items']}")
        
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        logger.info("Starting order confirmation process")
        context = self.get_context_data()
        # address = context.get('address')
                     
        cart = context.get('cart')
        if not cart or not cart.cartitems_set.exists():
            messages.error(request, '購物車に商品がありません')
            return redirect('hotel:cyumon_info')
        
        
        address_id = request.session.get('selected_address_id')
        address = get_object_or_404(UserAddresses, id=address_id, user=request.user)
            
        if not address:
            messages.error(request, '住所情報が見つかりません')
            return redirect('hotel:input_useraddresses')
                    
        total_price = context.get('total_price', 0)
        # total_price = context('total_price')
        kupon_amount = int(request.POST.get('kupon_amount', 0))
        actual_total_price = max(0, total_price - kupon_amount)
        
        logger.debug(f"Total price: {total_price}, Kupon amount: {kupon_amount}, Actual total price: {actual_total_price}")
        
        try: 
            for item in cart.cartitems_set.all():
                if item.quantity > item.product.stock:
                    raise Http404('予約注文処理でエラーが発生しました')


            order = Orders.objects.insert_cart(cart, address, actual_total_price)
            OrderItems.objects.insert_cart_items(cart, order)
            PlanName.objects.reduce_stock(cart)            
            # kupon_amount = int(kupon_amount) if kupon_amount else 0
            # actual_total_price = float(total_price or 0) - kupon_amount
            
            request.session['completed_order_id'] = order.id
            if 'kupon_amount' in request.session:
                del request.session['kupon_amount']

            cart.delete()
            
            logger.info("Redirecting to order success page")
            return redirect('hotel:order_success')
        
        except Exception as e:
            logger.error(f"Error during order processing: {str(e)}")
            messages.error(request, f'予約注文処理で予期せぬエラー発生しました: {str(e)}')
            
            return redirect('hotel:input_useraddresses')
    
            # return render(request, 'hotel/order_success.html', {'order': order})
    
                    
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
            order = Orders.objects.select_related('address').get(id=order_id, user=request.user)
            context = self.get_context_data(order=order)
            logger.info(f"Found order: {order.id}")
            del request.session['completed_order_id']
            # context = self.get_context_data(order=order)
            # return self.render_to_response(self.get_context_data(order=order))
            return self.render_to_response(context)
            
        except Orders.DoesNotExist:
            logger.error(f"Order with ID {order_id} not found for user {request.user}")
            messages.error(request, '注文が見つかりません')
            return redirect('hotel:cyumon_info')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = kwargs.get('order')
        if order:
            context['order'] = order
            context['order_items'] = order.orderitems_set.all()
            context['address'] = order.address
        return context
        
        # # 清除會話中的訂單ID
        # del request.session['completed_order_id']  
        
        # context = self.get_context_data(order=order)
        # return self.render_to_response(context)

class DeleteUserAddressView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = UserAddresses
    template_name = 'hotel/useraddresses_confirm_delete.html'
    success_url = reverse_lazy('hotel:input_useraddresses')
    
    def test_func(self):
        # 確保只有地址的所有者可以刪除
        try:
            obj = self.get_object()
            return obj.user == self.request.user
        except Http404:
            return False
    
    def get_object(self, queryset=None):
        # 明確地獲取對象，並確保它存在
        pk = self.kwargs.get('pk')
        try:
            obj = get_object_or_404(UserAddresses, pk=pk)
            if obj.user != self.request.user:
                raise Http404("このアドレスを削除する権限がありません。")
            return obj
        except Http404:
            return None
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return self.handle_no_permission()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['object'] = self.object
        return context

    def handle_no_permission(self):
        # 重定向到一個適當的頁面，例如錯誤頁面或首頁
        return redirect('hotel:input_useraddresses')
    
    # 這是不經過詢問直接刪除!
    # def post(self, request, *args, **kwargs):
    #        self.object = self.get_object()
    #        success_url = self.get_success_url()
    #        self.object.delete()
    #        return HttpResponseRedirect(success_url)
    
    
class OrdersListView(LoginRequiredMixin, ListView):
    model = Orders
    template_name = 'hotel/order_success_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Orders.objects.filter(user=self.request.user).order_by('-created_at')
    
    

class OrdersDetailView(LoginRequiredMixin, DetailView):
    model = Orders
    template_name = 'hotel/order_success_info.html'    
    context_object_name = 'order'
    
    def get_queryset(self):
        return Orders.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context['order_items'] = order.orderitems_set.all().select_related('product', 'product__hotel')
        context['address'] = order.address        
        return context
    

class DeleteOrderView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Orders
    template_name = 'hotel/delete_order.html'
    success_url = reverse_lazy('hotel:order_success_list')
    
    def test_func(self):
        order = self.get_object()
        return self.request.user == order.user
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.user == self.request.user:
            raise Http404
        return obj
        
    
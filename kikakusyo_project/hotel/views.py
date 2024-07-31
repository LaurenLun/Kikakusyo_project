from django.shortcuts import render, get_object_or_404, redirect
from .models import(
    HotelName, PlanName, HotelPictures, CyumonInfo, PlanListCalendar, 
    Carts, CartItems,
)
from .forms import(
    CyumonInfoUpdateForm,
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
        
        if self.object_list.exists():
            product_id = self.object_list.first().id
            context['is_added'] = CartItems.objects.filter(
                cart_id=self.request.user.id,
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
            
            cart, created = Carts.objects.get_or_create(user=request.user)
            cart_item, created = CartItems.objects.get_or_create(product=product, cart=cart)

            if not created:
                cart_item.quantity = quantity

            else:
                cart_item.quantity += quantity

            if cart_item.quantity > product.stock:
                return JsonResponse({'message': '部屋数を超えています'}, status=400)
            
            cart_item.save()
            
            return JsonResponse({'message': '希望するプランを予約注文に追加しました'})
        
        except ValueError:
            return JsonResponse({'message': '無効の数値です'}, status=400)
        
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")
            return JsonResponse({'message': str(e)}, status=400)
        
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



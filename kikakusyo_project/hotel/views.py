from django.shortcuts import render, get_object_or_404
from .models import HotelName, PlanName, HotelPictures, CyumonInfo
from django.views.generic.list import ListView
# from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
import os
import logging
logger = logging.getLogger(__name__)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hotel'] = self.hotel
        context['pictures'] = PlanName.objects.filter(hotel=self.hotel).order_by('order')
        order_by_price = self.request.GET.get('order_by_price', '1')
        if order_by_price == '2':
            context['plans'] = PlanName.objects.filter(hotel=context['hotel']).order_by('-price')
            context['descending'] = True
        else:
            context['plans'] = PlanName.objects.filter(hotel=context['hotel']).order_by('price')
            context['ascending'] = True
        return context

    def get_queryset(self):
        self.hotel = get_object_or_404(HotelName, pk=self.kwargs['pk'])
        query = PlanName.objects.filter(hotel=self.hotel).prefetch_related('pictures')
        
        for plan in query:
            logger.debug(f"Plan: {plan.name}, Pictures: {list(plan.pictures.all())}")
        # return super().get_queryset().filter(hotel=self.hotel)
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            query = query.order_by('price')
        elif order_by_price == '2':
            query = query.order_by('-price')
        
        logger.debug(f"order_by_price: {order_by_price}")
        
        return query
    
         
class CyumonInfoView(ListView):
    model = CyumonInfo
    template_name = 'hotel/cyumon_info.html'
    queryset = CyumonInfo.objects.all()
    
    def get_queryset(self):
        return CyumonInfo.objects.all()
    


    
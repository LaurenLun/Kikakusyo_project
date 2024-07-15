from django.contrib import admin
from .models import(
    HotelName, PlanName, HotelPictures,
)
# Register your models here.

admin.site.register(
    [HotelName, PlanName, HotelPictures]
)
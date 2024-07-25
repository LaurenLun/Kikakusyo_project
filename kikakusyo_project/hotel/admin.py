from django.contrib import admin
from .models import(
    HotelName, PlanName, HotelPictures, PlanPictures,
)
# Register your models here.

admin.site.register(
    [HotelName, PlanName, HotelPictures]
)
    
@admin.register(PlanPictures)
class PlanPicturesAdmin(admin.ModelAdmin):
    list_display = ('plan', 'image', 'order')
    list_editable = ('order',)
    list_filter = ('plan',)
    search_fields = ('plan', 'order')
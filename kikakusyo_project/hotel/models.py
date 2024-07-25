from django.db import models
from datetime import datetime
from accounts.models import Users
# from .forms import HotelForm

# Create your models here.

class HotelName(models.Model):
    name = models.CharField(max_length=1000)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'hotel_name'
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
class PlanName(models.Model):
    name = models.CharField(max_length=1000)
    people = models.IntegerField()
    room_type = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    hotel = models.ForeignKey(HotelName, on_delete=models.CASCADE, default=1)
    stock = models.PositiveIntegerField(default=0)
    order = models.IntegerField(default=0)
    # picture = models.FileField(upload_to='hotel_pictures/', null=True)
    
    class Meta:
        db_table = 'plan_name'
        ordering = ['order']
    
    def __str__(self):
        return self.name

class HotelPictures(models.Model):
    image = models.ImageField(upload_to='hotel_pictures/', null=True)
    hotel = models.ForeignKey(
        HotelName, related_name='pictures', on_delete=models.CASCADE
    )
    order = models.IntegerField()
    
    class Meta:
        db_table = 'hotel_pictures'
        ordering = ['order']

    def __str__(self):
        return self.hotel.name + ':' + str(self.order)
        # return f"(self.hotel.name) - Picture {self.order}"

class PlanPictures(models.Model):
    plan = models.ForeignKey(PlanName, on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to='plan_pictures/')
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Plan Picture'
        verbose_name_plural = 'Plan Pictures'
        ordering = ['plan', 'order']
      
    def __str__(self):
        return f"(self.plan.name) - Picture {self.order}"

class CyumonInfo(models.Model):
    checkin = models.DateTimeField(default=datetime.now())
    checkout = models.DateTimeField(default=datetime.now())
    room_type = models.CharField(max_length=50)
    price = models.IntegerField()
    stock = models.IntegerField()
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"Reservation for {self.room_type}"
    
class Carts(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete = models.CASCADE,
        primary_key = True
    )
    
    class Meta:
        db_table = 'carts'
        
class CartItems(models.Model):
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(
        PlanName, on_delete=models.CASCADE
    )
    cart = models.ForeignKey(
        Carts, on_delete=models.CASCADE
    )
    
    class Meta:
        db_table = 'cart_items'
        unique_together = [['product', 'cart']]
from django.db import models
from datetime import time, datetime
from accounts.models import Users
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
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
    
class PlanNameManager(models.Manager):
    
    def reduce_stock(self, cart):
        if not cart.id:
            cart.save()
        for item in cart.cartitems_set.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
    
class PlanName(models.Model):
    name = models.CharField(max_length=1000)
    people = models.IntegerField()
    room_type = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=5, decimal_places=0)
    hotel = models.ForeignKey(HotelName, on_delete=models.CASCADE, default=1)
    stock = models.PositiveIntegerField(default=0)
    order = models.IntegerField(default=0)
    checkin = models.DateField(null=True, blank=True)
    checkout = models.DateField(null=True, blank=True)
    kupon = models.IntegerField(default=0)
    # picture = models.FileField(upload_to='hotel_pictures/', null=True)
    objects = PlanNameManager()

    
    class Meta:
        db_table = 'plan_name'
        ordering = ['order']
    
    def __str__(self):
        return self.name

class HotelPictures(models.Model):
    image = models.FileField(upload_to='hotel_pictures/', null=True)
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
    image = models.FileField(upload_to='plan_pictures/')
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Plan Picture'
        verbose_name_plural = 'Plan Pictures'
        ordering = ['plan', 'order']
      
    def __str__(self):
        return f"(self.plan.name) - Picture {self.order}"

class CyumonInfo(models.Model):
    checkin = models.DateTimeField(default=datetime.now)
    checkout = models.DateTimeField(default=datetime.now)
    room_type = models.CharField(max_length=50)
    price = models.IntegerField()
    stock = models.IntegerField()
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"Reservation for {self.room_type}"
    
    # def get_context_data(self):
    #     context = {
    #         'checkin': self.product.checkin,
    #         'checkout': self.product.checkout,
    #         'hotel_name': self.hotel_name,
    #     }
    #     return context
    
class Carts(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
    
    @property
    def id(self):
        return self.user_id
        
class CartItemsManager(models.Manager):
    def add_or_update_item(self, product_id, quantity, cart):
        cart_item, created = self.get_or_create(product_id=product_id, cart=cart)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return cart_item
       
    def save_item(self, product_id, quantity, cart):
        c = self.model(quantity=quantity, product_id=product_id, cart=cart)
        c.save()
        
class CartItems(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(
        PlanName, on_delete=models.CASCADE
    )
    cart = models.ForeignKey(
        Carts, on_delete=models.CASCADE
    )
    objects = CartItemsManager()
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ('product', 'cart')
        
    def get_context_data(self):
        context = {
            'checkin': self.product.checkin,
            'checkout': self.product.checkout,
        }
        return context

class PlanListCalendar(models.Model):
    plans = models.ForeignKey(PlanName, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()


class UserAddresses(models.Model):
    last_name = models.CharField(max_length=10)
    first_name = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=8)
    address = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=13)
    user = models.ForeignKey(
        Users,
        on_delete = models.CASCADE, 
    )
    
    class Meta:
        db_table = 'useraddresses'
        unique_together = [
            ['last_name', 'first_name', 'zip_code', 'address', 'phone_number', 'user']
        ]
        
    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.zip_code} {self.address} { self.phone_number}'


class OrdersManager(models.Manager):
    
    def insert_cart(self, cart, useraddresses, total_price):
        if not cart.id:
            cart.save()
        return self.create(
            total_price = total_price,
            address = useraddresses,
            user = cart.user,
        )

class Orders(models.Model):
    total_price = models.PositiveIntegerField()
    address = models.ForeignKey(
        UserAddresses,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    objects = OrdersManager()
    class Meta:
        db_table = 'orders'
    

class OrderItemsManager(models.Manager):
    
    def insert_cart_items(self, cart, order):
        if not cart.id:
            cart.save()
        for item in cart.cartitems_set.all():
            self.create(
                quantity = item.quantity,
                product = item.product,
                order = order,
            )



class OrderItems(models.Model):
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(
        PlanName,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        Orders, on_delete=models.CASCADE
    )
    objects = OrderItemsManager()
    
    class Meta:
        db_table = 'order_items'
        unique_together = [['product', 'order']]
        
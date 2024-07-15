from django.db import models

# Create your models here.

class HotelName(models.Model):
    name = models.CharField(max_length=1000)
    
    class Meta:
        db_table = 'hotel_name'
    
    def __str__(self):
        return self.name
    
class PlanName(models.Model):
    name = models.CharField(max_length=1000)
    people = models.IntegerField()
    room_type = models.CharField(max_length=1000)
    price = models.IntegerField()
    
    class Meta:
        db_table = 'plan_name'
    
    def __str__(self):
        return self.name

class HotelPictures(models.Model):
    picture = models.FileField(upload_to='hotel_pictures/')
    hotel = models.ForeignKey(
        HotelName, on_delete=models.CASCADE
    )
    order = models.IntegerField()
    
    class Meta:
        db_table = 'hotel_pictures'
        ordering = ['order']

    def __str__(self):
        return self.hotel.name + ':' + str(self.order)
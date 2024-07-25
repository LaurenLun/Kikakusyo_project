# Generated by Django 5.0.6 on 2024-07-24 11:28

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0008_alter_planpictures_options_planpictures_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotelpictures',
            name='picture',
        ),
        migrations.AddField(
            model_name='hotelpictures',
            name='image',
            field=models.ImageField(null=True, upload_to='hotel_pictures/'),
        ),
        migrations.AlterField(
            model_name='cyumoninfo',
            name='checkin',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 24, 20, 28, 32, 253116)),
        ),
        migrations.AlterField(
            model_name='cyumoninfo',
            name='checkout',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 24, 20, 28, 32, 253116)),
        ),
        migrations.AlterField(
            model_name='hotelpictures',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='hotel.hotelname'),
        ),
    ]

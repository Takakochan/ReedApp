from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


class Reedsetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    temperature = models.BooleanField(default=True)
    humidity = models.BooleanField(default=True)
    cane_brand = models.BooleanField(default=True)
    harvest_year = models.BooleanField(default=True)
    profile_model = models.BooleanField(default=True)
    gouging_machine = models.BooleanField(default=True)
    cane_diamater = models.BooleanField(default=True)
    thickness = models.BooleanField(default=True)
    hardness = models.BooleanField(default=True)
    flexibility = models.BooleanField(default=True)
    density = models.BooleanField(default=True)
    shaper = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#data_preference11個　12thJune2025時点
data_preference = [
    ('temperature', 'Temperature'),
    ('humidity', 'Humidity'),
    ('cane_brand', 'Cane Brand'),
    ('harvest_year', 'Harvest Year'),
    ('gouging_machine', 'Gounging Machine'),
    ('profile_model', 'Profile Model'),
    ('cane_diamater', 'Diamater'),
    ('thickness', 'Thickness'),
    ('hardness', 'Hardness'),
    ('flexibility', 'Flexibility'),
    ('density', 'Density'),
    ('shaper', 'Shaper'),
]


class Checkbox_for_setting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkboxsetting = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    #temperature = models.BooleanField(default=True)
    #humidity = models.BooleanField(default=True)
    #cane_brand = models.BooleanField(default=True)
    #harvest_year = models.BooleanField(default=True)
    #gouging_machine = models.BooleanField(default=True)
    #cane_diamater = models.BooleanField(default=True)
    #thickness = models.BooleanField(default=True)
    #hardness = models.BooleanField(default=True)
    #flexibility = models.BooleanField(default=True)
    #density = models.BooleanField(default=True)
    #shaper = models.BooleanField(default=True)

    #created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)

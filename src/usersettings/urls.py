from django.urls import path
from . import views

app_name = 'usersetting'

urlpatterns = [
    path('', views.land_demand_form, name='top'),
]
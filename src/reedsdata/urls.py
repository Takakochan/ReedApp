from django.urls import path
from .views import data_entry, reedsdata_list, edit_reedsdata, delete_reedsdata, get_weather_data, add_batch, data_overview, save_parameter_settings, get_reed_data

#from .views import ReedsdataListView, ReedsdataCreateView, ReedsdataUpdateView, ReedsdataDeleteView

app_name = 'reeds'

urlpatterns = [
    path('add/', data_entry, name='add'),
    path('add-batch/', add_batch, name='add_batch'),
    path('overview/', data_overview, name='data_overview'),
    path('list/', reedsdata_list, name='reedsdata_list'),
    path('edit/<int:pk>/', edit_reedsdata, name='edit_reedsdata'),
    path('delete/<int:pk>/', delete_reedsdata, name='delete_reedsdata'),
    path('get-weather/', get_weather_data, name='get_weather'),
    path('save-parameter-settings/', save_parameter_settings, name='save_parameter_settings'),
    path('get-reed-data/', get_reed_data, name='get_reed_data'),
]

from django.urls import path
from .views import data_entry, reedsdata_list, edit_reedsdata, delete_reedsdata

#from .views import ReedsdataListView, ReedsdataCreateView, ReedsdataUpdateView, ReedsdataDeleteView

app_name = 'reeds'

urlpatterns = [
    path('add/', data_entry, name='add'),
    path('list/', reedsdata_list, name='reedsdata_list'),
    path('edit/<int:pk>/', edit_reedsdata, name='edit_reedsdata'),
    path('delete/<int:pk>/', delete_reedsdata, name='delete_reedsdata'),
]

from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.account_view, name='account'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
    path('statistics/', views.account_statistics_view, name='statistics'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    # Data export endpoints
    path('export/csv/', views.export_data_csv, name='export_csv'),
    path('export/excel/', views.export_data_excel, name='export_excel'),
    path('export/json/', views.export_data_json, name='export_json'),
]
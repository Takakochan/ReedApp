"""
URL configuration for reedmanage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import (
    home_view, login_view, signup, verify_email_view,
    privacy_policy_view, terms_of_service_view,
    test_404_view, test_500_view
)
from .health_check import health_check, simple_health_check, detailed_health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('signup', signup, name='signup'),
    path('login', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('verify-email/<uidb64>/<token>/', verify_email_view, name='verify_email'),

    # Legal pages
    path('legal/privacy/', privacy_policy_view, name='privacy_policy'),
    path('legal/terms/', terms_of_service_view, name='terms_of_service'),

    #path('evaluate/', include('reedsdata.urls', namespace='reeds')),
    path('reeds/', include('reedsdata.urls', namespace='reeds')),
    path('settings/', include('usersettings.urls', namespace='setting')),
    path('contact/', include('contact.urls', namespace='contact')),
    path('account/', include('account.urls', namespace='account')),
    path("__reload__/", include("django_browser_reload.urls")),

    # Health check endpoints for production monitoring
    path('health/', health_check, name='health_check'),
    path('health/simple/', simple_health_check, name='simple_health_check'),
    path('health/detailed/', detailed_health_check, name='detailed_health_check'),

    # Test error pages (development only - remove before production)
    path('test-404/', test_404_view, name='test_404'),
    path('test-500/', test_500_view, name='test_500'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'reedmanage.views.custom_404'
handler500 = 'reedmanage.views.custom_500'

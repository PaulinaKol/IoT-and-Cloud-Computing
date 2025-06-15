from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('my_devices/', views.my_devices, name='my_devices'),
    path('add_device/', views.add_device, name='add_device'),
    path('delete_device/<str:device_id>/', views.delete_device, name='delete_device'),
    path('rename_device/', views.rename_device, name='rename_device'),
    path('delete_notifications/', views.delete_notifications, name='delete_notifications'),
]
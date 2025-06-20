from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import change_password

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('my_devices/', views.my_devices, name='my_devices'),
    path('add_device/', views.add_device, name='add_device'),
    path('ajax_delete_device/', views.ajax_delete_device, name='ajax_delete_device'),
    path('ajax_rename_device/', views.ajax_rename_device, name='ajax_rename_device'),
    path('delete_notifications/', views.delete_notifications, name='delete_notifications'),
    path('notifications_table/', views.notifications_table, name='notifications_table'),
    path('devices_list/', views.devices_list, name='devices_list'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('ajax_get_user_notification_settings/', views.ajax_get_user_notification_settings, name='ajax_get_user_notification_settings'),
    path('ajax_set_user_notification_settings/', views.ajax_set_user_notification_settings, name='ajax_set_user_notification_settings'),
    path('api/device_event/', views.device_event_api, name='device_event_api'),
    path('change_password/', change_password, name='change_password'),
]
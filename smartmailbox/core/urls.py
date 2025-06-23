from django.urls import path
from .views import device_views, user_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # === Ogólne ===
    path('', user_views.home_redirect, name='home'),

    # === Użytkownik – rejestracja, logowanie, wylogowanie ===
    path('register/', user_views.register, name='register'),
    path('login/', user_views.CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset/password_reset.html',
        email_template_name='password_reset/password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset/password_reset_complete.html'), name='password_reset_complete'),

    # === Aktywacja i ustawienia konta ===
    path('activate/', user_views.activate_account, name='activate_account'),
    path('user_settings/', user_views.user_settings, name='user_settings'),
    path('ajax_get_user_notification_settings/', user_views.ajax_get_user_notification_settings, name='ajax_get_user_notification_settings'),
    path('ajax_set_user_notification_settings/', user_views.ajax_set_user_notification_settings, name='ajax_set_user_notification_settings'),

    # === Zmiana danych użytkownika ===
    path('change_password/', user_views.change_password, name='change_password'),
    path('change_email/', user_views.change_email, name='change_email'),
    path('delete_account/', user_views.delete_account, name='delete_account'),

    # === Urządzenia – obsługa podstawowa ===
    path('my_devices/', device_views.my_devices, name='my_devices'),
    path('add_device/', device_views.add_device, name='add_device'),

    # === Ajax/API – urządzenia ===
    path('ajax_delete_device/', device_views.ajax_delete_device, name='ajax_delete_device'),
    path('ajax_rename_device/', device_views.ajax_rename_device, name='ajax_rename_device'),
    path('devices_list/', device_views.devices_list, name='devices_list'),

    # === Notyfikacje ===
    path('notifications_table/', device_views.notifications_table, name='notifications_table'),
    path('delete_notifications/', device_views.delete_notifications, name='delete_notifications'),

    # === API dla urządzenia ===
    path('api/device_event/', device_views.device_event_api, name='device_event_api'),
]

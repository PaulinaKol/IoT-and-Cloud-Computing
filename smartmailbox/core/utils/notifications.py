import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmailbox.settings')
django.setup()

from core.models import Device, DeviceNotification
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from core.models import DeviceNotification, UserNotificationSettings
from django.contrib.auth.models import User

def create_email(subject, message, recipient):
    """
    Wysyła pojedynczego maila. 
    """
    send_mail(
        subject,
        message,
        None,
        [recipient],
        fail_silently=True
    )

def create_device_notification(device, msg_type, previous_weight=None, current_weight=None):
    """
    Tylko tworzy wpis DeviceNotification — bez wysyłania maila.
    """
    if msg_type in ['MAIL_IN', 'MAIL_OUT']:
        DeviceNotification.objects.create(
            device=device,
            msg_type=msg_type,
            previous_weight=previous_weight,
            current_weight=current_weight
        )

def create_notification_and_email(device, msg_type, previous_weight=None, current_weight=None, extra_info=None):
    """
    Oryginalna funkcja — tworzy wpis do DeviceNotification i wysyła email
    """
    if msg_type in ['MAIL_IN', 'MAIL_OUT']:
        create_device_notification(device, msg_type, previous_weight, current_weight)

    user = device.owner
    now = timezone.now()
    try:
        settings = UserNotificationSettings.objects.get(user=user)
    except UserNotificationSettings.DoesNotExist:
        settings = None

    if not settings or not user.email:
        return

    if msg_type == 'MAIL_IN' and settings.notify_mail_in:
        subject = "📬 Nowa przesyłka w Twojej skrzynce!"
        message = (
            f"Cześć {user.username}!\n\n"
            f"W Twojej skrzynce '{device.name}' wykryto wrzucenie przesyłki.\n"
            f"Waga przed: {previous_weight} g\n"
            f"Waga po: {current_weight} g\n\n"
            f"Dziękujemy za korzystanie ze SmartMailbox!"
        )
        create_email(subject, message, user.email)
        return

    if msg_type == 'MAIL_OUT' and settings.notify_mail_out:
        subject = "📭 Przesyłka została wyjęta"
        message = (
            f"Cześć {user.username}!\n\n"
            f"Z Twojej skrzynki '{device.name}' wyjęto przesyłkę.\n"
            f"Waga przed: {previous_weight} g\n"
            f"Waga po: {current_weight} g\n\n"
            f"Dziękujemy za korzystanie ze SmartMailbox!"
        )
        create_email(subject, message, user.email)
        return

    if msg_type == 'LOW_BATTERY' and settings.notify_low_battery:
        last_sent = device.last_low_battery_email
        if last_sent is None or now - last_sent > timedelta(minutes=5):
            subject = "⚠️ Niski poziom baterii w Twojej skrzynce"
            message = (
                f"Cześć {user.username}!\n\n"
                f"W urządzeniu '{device.name}' poziom baterii spadł do {extra_info['battery_level']}%.\n"
                f"Zalecamy wymianę baterii, aby urządzenie działało prawidłowo.\n\n"
                f"SmartMailbox"
            )
            create_email(subject, message, user.email)
            device.last_low_battery_email = now
            device.save(update_fields=['last_low_battery_email'])
        return

    if msg_type == 'CONNECTION_LOST' and settings.notify_lost_connection:
        last_sent = device.last_connection_lost_email
        if last_sent is None or now - last_sent > timedelta(minutes=5):
            subject = "⚠️ Utrata połączenia z urządzeniem!"
            message = (
                f"Cześć {user.username}!\n\n"
                f"Twoje urządzenie '{device.name}' przestało odpowiadać i mogło stracić połączenie z siecią.\n"
                f"Prosimy sprawdzić stan urządzenia.\n\n"
                f"SmartMailbox"
            )
            create_email(subject, message, user.email)
            device.last_connection_lost_email = now
            device.save(update_fields=['last_connection_lost_email'])
        return

def send_activation_email(user):
    """
    Wysyła kod aktywacyjny na email użytkownika (do aktywacji konta).
    """
    profile = user.userprofile
    code = profile.generate_activation_code()
    subject = "Twój kod aktywacyjny"
    message = f"Twój kod aktywacyjny: {code}"
    create_email(subject, message, user.email)
    return code
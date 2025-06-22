import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from core.models import DeviceNotification, UserNotificationSettings


def get_user_notification_settings(user):
    try:
        return UserNotificationSettings.objects.get(user=user)
    except UserNotificationSettings.DoesNotExist:
        logging.warning(f"Brak ustawień notyfikacji dla usera {user.id}")
        return None

def create_email(subject, message, recipient):
    send_mail(
        subject,
        message,
        None,
        [recipient],
        fail_silently=True
    )

def create_device_notification(device, msg_type, previous_weight=None, current_weight=None):
    if msg_type in ['MAIL_IN', 'MAIL_OUT']:
        DeviceNotification.objects.create(
            device=device,
            msg_type=msg_type,
            previous_weight=previous_weight,
            current_weight=current_weight
        )

def send_activation_email(user):
    profile = user.userprofile
    code = profile.generate_activation_code()
    subject = "Twój kod aktywacyjny"
    message = f"Twój kod aktywacyjny: {code}"
    create_email(subject, message, user.email)
    return code

def get_mail_in_message(user, device, previous_weight, current_weight):
    subject = "📬 Nowa przesyłka w Twojej skrzynce!"
    message = (
        f"Cześć {user.username}!\n\n"
        f"W Twojej skrzynce '{device.name}' wykryto wrzucenie przesyłki.\n"
        f"Waga przed: {previous_weight} g\n"
        f"Waga po: {current_weight} g\n\n"
        f"Dziękujemy za korzystanie ze SmartMailbox!"
    )
    return subject, message

def get_mail_out_message(user, device, previous_weight, current_weight):
    subject = "📭 Przesyłka została wyjęta"
    message = (
        f"Cześć {user.username}!\n\n"
        f"Z Twojej skrzynki '{device.name}' wyjęto przesyłkę.\n"
        f"Waga przed: {previous_weight} g\n"
        f"Waga po: {current_weight} g\n\n"
        f"Dziękujemy za korzystanie ze SmartMailbox!"
    )
    return subject, message

def get_low_battery_message(user, device, battery_level):
    subject = "⚠️ Niski poziom baterii w Twojej skrzynce"
    message = (
        f"Cześć {user.username}!\n\n"
        f"W urządzeniu '{device.name}' poziom baterii spadł do {battery_level}%.\n"
        f"Zalecamy wymianę baterii, aby urządzenie działało prawidłowo.\n\n"
        f"SmartMailbox"
    )
    return subject, message

def get_connection_lost_message(user, device):
    subject = "⚠️ Utrata połączenia z urządzeniem!"
    message = (
        f"Cześć {user.username}!\n\n"
        f"Twoje urządzenie '{device.name}' przestało odpowiadać i mogło stracić połączenie z siecią.\n"
        f"Prosimy sprawdzić stan urządzenia.\n\n"
        f"SmartMailbox"
    )
    return subject, message

def create_notification_and_email(device, msg_type, previous_weight=None, current_weight=None, extra_info=None):
    user = device.owner
    now = timezone.now()
    settings = get_user_notification_settings(user)

    if not settings or not user.email:
        logging.warning(f"Brak maila lub ustawień powiadomień dla usera {user.id}")
        return

    if msg_type == 'MAIL_IN' and settings.notify_mail_in:
        create_device_notification(device, msg_type, previous_weight, current_weight)
        subject, message = get_mail_in_message(user, device, previous_weight, current_weight)
        create_email(subject, message, user.email)
        return

    if msg_type == 'MAIL_OUT' and settings.notify_mail_out:
        create_device_notification(device, msg_type, previous_weight, current_weight)
        subject, message = get_mail_out_message(user, device, previous_weight, current_weight)
        create_email(subject, message, user.email)
        return

    if msg_type == 'LOW_BATTERY' and settings.notify_low_battery:
        last_sent = device.last_low_battery_email
        if last_sent is None or now - last_sent > timedelta(minutes=5):
            subject, message = get_low_battery_message(user, device, extra_info['battery_level'] if extra_info else '??')
            create_email(subject, message, user.email)
            device.last_low_battery_email = now
            device.save(update_fields=['last_low_battery_email'])
        return

    if msg_type == 'CONNECTION_LOST' and settings.notify_lost_connection:
        last_sent = device.last_connection_lost_email
        if last_sent is None or now - last_sent > timedelta(minutes=5):
            subject, message = get_connection_lost_message(user, device)
            create_email(subject, message, user.email)
            device.last_connection_lost_email = now
            device.save(update_fields=['last_connection_lost_email'])
        return



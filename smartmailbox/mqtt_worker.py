import os
import django
import json
import paho.mqtt.client as mqtt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmailbox.settings')
django.setup()

from core.models import Device, DeviceNotification

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "mailbox/device_events"

def on_connect(client, userdata, flags, rc):
    print("Połączono z MQTT, kod: " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Otrzymano wiadomość: {msg.payload}")
    try:
        data = json.loads(msg.payload.decode())
        device_id = data.get('device_id')
        security_code = data.get('security_code')
        battery_level = data.get('battery_level')
        timestamp = data.get('timestamp')
        weight = data.get('weight', None)
        msg_type = data.get('msg_type', None)

        device = Device.objects.filter(device_id=device_id, security_code=security_code).first()
        if device:
            if battery_level is not None:
                device.battery_level = battery_level

            previous_weight = getattr(device, 'detected_weight', 0) or 0
            if weight is not None:
                device.detected_weight = weight

            dt = parse_datetime(timestamp)
            if dt and is_naive(dt):
                from django.utils import timezone
                dt = make_aware(dt, timezone.get_current_timezone())

            if msg_type == "HEARTBEAT":
                device.last_heartbeat_time = dt
                print(f"[HEARTBEAT] Urządzenie {device_id}: sygnał heartbeat, waga: {weight}g.")
            elif msg_type in ["MAIL_IN", "MAIL_OUT"]:
                DeviceNotification.objects.create(
                    device=device,
                    msg_type=msg_type,
                    previous_weight=previous_weight,
                    current_weight=weight if weight is not None else previous_weight
                )
            else:
                print(f"[INNY_TYP] msg_type={msg_type}, dane={data}")

            device.save()
        else:
            print("Nie znaleziono urządzenia lub kod nieprawidłowy.")
    except Exception as e:
        print(f"Błąd przy przetwarzaniu wiadomości: {e}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()

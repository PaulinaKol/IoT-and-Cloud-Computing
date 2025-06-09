import os
import django
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# Ustawienie Django settings (upewnij się, że ścieżka jest poprawna!)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmailbox.settings')
django.setup()

from core.models import Device

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

        # Znajdź urządzenie po device_id i security_code
        device = Device.objects.filter(device_id=device_id, security_code=security_code).first()
        if device:
            device.battery_level = battery_level
            device.last_package_time = timestamp
            device.save()
            print(f"Zaktualizowano urządzenie {device_id}")
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

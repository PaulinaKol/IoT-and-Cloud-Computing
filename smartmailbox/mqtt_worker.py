import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartmailbox.settings')
django.setup()
import json
import requests
import paho.mqtt.client as mqtt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive

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
        send_event_to_backend(data)
    except Exception as e:
        print("Błąd dekodowania payload:", e)

def send_event_to_backend(payload):
    url = "http://localhost:8000/api/device_event/"
    headers = {
        "Authorization": "Token TEMP_TEST_TOKEN",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=3)
        print("Odpowiedź backendu:", resp.status_code, resp.json())
    except Exception as e:
        print("Błąd REST API:", e)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()

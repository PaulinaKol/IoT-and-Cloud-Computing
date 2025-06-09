import paho.mqtt.client as mqtt
import random
import time
from datetime import datetime

BROKER = "test.mosquitto.org"  # Jeśli używasz brokera lokalnie. Zmień na adres brokera, jeśli korzystasz z innego.
PORT = 1883
TOPIC = "mailbox/device_events"

def main():
    device_id = input("Podaj ID urządzenia: ")
    security_code = input("Podaj kod bezpieczeństwa: ")

    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    while True:
        input("Naciśnij Enter, aby zasymulować wrzucenie paczki...")

        battery = random.randint(10, 100)
        payload = {
            "device_id": device_id,
            "security_code": security_code,
            "battery_level": battery,
            "timestamp": datetime.now().isoformat()
        }

        # Wysyłka jako string – w realnym projekcie można użyć JSON
        import json
        client.publish(TOPIC, json.dumps(payload))
        print(f"Wysłano powiadomienie: {payload}")

        time.sleep(1)

if __name__ == "__main__":
    main()

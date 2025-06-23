import time
import logging
import threading
import json
import atexit
import requests
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("mqtt_worker")

exit_flag = threading.Event()

executor = ThreadPoolExecutor(max_workers=10)
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "mailbox/device_events"

def on_connect(client, userdata, flags, rc):
    logger.info(f"Połączono z MQTT, kod: {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    logger.info(f"Otrzymano wiadomość: {msg.payload}")
    try:
        data = json.loads(msg.payload.decode())
        executor.submit(send_event_to_backend, data)
    except Exception as e:
        logger.error(f"Błąd dekodowania payload: {e}")

def send_event_to_backend(payload, max_retries=3, delay=2):
    url = "http://localhost:8000/api/device_event/"
    headers = {
        "Authorization": "Token TEMP_TEST_TOKEN",
        "Content-Type": "application/json"
    }
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=3)
            try:
                logger.info(f"Odpowiedź backendu: {resp.status_code} {resp.json()}")
            except Exception:
                logger.info(f"Odpowiedź backendu: {resp.status_code} {resp.text}")
            return
        except Exception as e:
            logger.warning(f"Błąd REST API (próba {attempt} z {max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Ponawianie za {delay} sekundy...")
                time.sleep(delay)
            else:
                logger.error("Nie udało się połączyć z backendem po kilku próbach.")

def close_executor():
    executor.shutdown(wait=True)
    logger.info("Zamknięto executor, wszystkie zadania zakończone.")

atexit.register(close_executor)

def input_thread():
    while not exit_flag.is_set():
        try:
            cmd = input()
            if cmd.strip().lower() in ['stop', 'exit', 'quit']:
                logger.info("Otrzymano polecenie zakończenia programu.")
                exit_flag.set()
                break
        except EOFError:
            # Np. Ctrl+D
            logger.info("EOF – kończenie programu.")
            exit_flag.set()
            break

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    threading.Thread(target=input_thread, daemon=True).start()

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        logger.info("mqtt_worker działa. Naciśnij Ctrl+C lub wpisz 'stop' by zakończyć.")
        while not exit_flag.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Przerwano przez Ctrl+C. Kończę pracę.")
        exit_flag.set()
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Rozłączono z MQTT brokera.")


if __name__ == "__main__":
    main()

import os
import time
import logging
import threading
import json
import atexit
import requests
import signal
import sys
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("mqtt_worker")

exit_flag = threading.Event()

executor = ThreadPoolExecutor(max_workers=int(os.getenv('MQTT_WORKER_THREADS', '10')))
BROKER = os.getenv('MQTT_BROKER', '52.139.28.127')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', 'smartmailbox/device_events')
BACKEND_URL = os.getenv('BACKEND_URL', 'https://smartmailbox-dtcuf3gdajhdc7ez.canadacentral-01.azurewebsites.net/api/device_event/')
API_TOKEN = os.getenv('API_TOKEN', 'TEMP_TEST_TOKEN')
VERIFY_SSL = os.getenv('VERIFY_SSL', 'False').lower() in ['1', 'true', 'yes']

def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker: {BROKER}:{PORT}, code: {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    logger.info(f"Received MQTT message: {msg.payload}")
    try:
        data = json.loads(msg.payload.decode())
        executor.submit(send_event_to_backend, data)
    except Exception as e:
        logger.error(f"Payload decode error: {e}")

def send_event_to_backend(payload, max_retries=3, delay=2):
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=5, verify=VERIFY_SSL)
            try:
                logger.info(f"Backend response: {resp.status_code} {resp.json()}")
            except Exception:
                logger.info(f"Backend response: {resp.status_code} {resp.text}")
            return
        except Exception as e:
            logger.warning(f"REST API error (attempt {attempt} of {max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Failed to connect to backend after several attempts.")

def close_executor():
    executor.shutdown(wait=True)
    logger.info("Executor closed, all tasks completed.")

atexit.register(close_executor)

def handle_sigterm(signum, frame):
    logger.info("Received termination signal. Shutting down gracefully...")
    exit_flag.set()

def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm) # Optional: Ctrl+C locally

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        logger.info("mqtt_worker started and running. Waiting for messages...")
        while not exit_flag.is_set():
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        exit_flag.set()
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Disconnected from MQTT broker.")

if __name__ == "__main__":
    main()

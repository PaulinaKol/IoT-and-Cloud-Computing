import os
import time
import json
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timezone


ASCII_ART = r"""
                            _       _             
                           | |     | |            
  ___ _   _ _ __ ___  _   _| | __ _| |_ ___  _ __ 
 / __| | | | '_ ` _ \| | | | |/ _` | __/ _ \| '__|
 \__ \ |_| | | | | | | |_| | | (_| | || (_) | |   
 |___/\__, |_| |_| |_|\__,_|_|\__,_|\__\___/|_|   
       __/ |                                      
      |___/                                       
"""

BROKER = "52.139.28.127" 
PORT = 1883
TOPIC = "smartmailbox/device_events"

def heartbeat_loop(client, device_id_ref, security_code_ref, battery_ref, weight_ref, running_flag, paused_flag):
    while running_flag["run"]:
        if not paused_flag["paused"]:
            payload = {
                "device_id": device_id_ref["value"],
                "security_code": security_code_ref["value"],
                "battery_level": battery_ref["value"],
                "weight": weight_ref["value"],
                "msg_type": "HEARTBEAT",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.publish(TOPIC, json.dumps(payload))
            #print("Wysłano heartbeat...") #FOR DEBUG
        for _ in range(10):  # 10 x 1 sekunda, żeby móc przerwać szybko pętlę przy wychodzeniu
            if not running_flag["run"]:
                break
            time.sleep(1)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title(id_value=None, code_value=None, battery_value=None, weight_value=None):
    clear_screen()
    print(ASCII_ART)
    print_status_bar(id_value, code_value, battery_value, weight_value)
    print()

def print_status_bar(id_value, code_value, battery_value, weight_value):
    status = (
        f"| ID: {id_value if id_value else '...'} "
        f"| Kod Bezp: {code_value if code_value else '...'} "
        f"| Stan Baterii: {battery_value if battery_value is not None else '...'} "
        f"| Wykrywana waga: {weight_value if weight_value is not None else '...'} g |"
    )
    print(status)

def change_battery_level(device_id, security_code, battery):
    while True:
        show_title(device_id, security_code, battery)
        new_battery = input("Wprowadź nowy stan baterii (1-100): ")
        try:
            new_battery = int(new_battery)
            if 1 <= new_battery <= 100:
                return new_battery
            else:
                print("Stan baterii musi być liczbą od 1 do 100.")
                time.sleep(1)
        except ValueError:
            print("Wprowadź poprawną liczbę.")
            time.sleep(1)

def change_detected_weight(device_id, security_code, battery, weight):
    while True:
        show_title(device_id, security_code, battery, weight)
        new_weight = input("Wprowadź nową wykrywaną wagę (w gramach, >=0): ")
        try:
            new_weight = float(new_weight.replace(',', '.'))
            if new_weight >= 0:
                return new_weight
            else:
                print("Waga musi być nieujemna.")
                time.sleep(1)
        except ValueError:
            print("Wprowadź poprawną liczbę.")
            time.sleep(1)

def get_device_info():
    device_id = None
    security_code = None
    battery = None

    show_title(device_id, security_code, battery)
    device_id = input("Podaj ID urządzenia: ")

    show_title(device_id, security_code, battery)
    security_code = input("Podaj kod bezpieczeństwa urządzenia: ")

    battery = change_battery_level(device_id, security_code, battery)

    return device_id, security_code, battery

def show_main_menu(device_id, security_code, battery, weight):
    show_title(device_id, security_code, battery, weight)
    print("Wprowadź numer opcji i naciśnij Enter:\n")
    print("1. Symuluj wrzucenie paczki")
    print("2. Symuluj wyciągnięcie paczki / paczek")
    print("3. Zmień stan baterii")
    print("4. Symuluj zaprzestanie sygnału heartbeat")
    print("5. Zmień wykrywaną wagę")
    print("0. Wyjdź z programu\n")

def simulate_package_drop(client, device_id, security_code, battery, weight):
    while True:
        show_title(device_id, security_code, battery, weight)
        weight_input = input("Podaj wagę wrzuconej przesyłki: ")
        try:
            added_weight = float(weight_input.replace(',', '.'))
            if added_weight > 0:
                break
            else:
                print("Waga musi być liczbą dodatnią.")
                time.sleep(1)
        except ValueError:
            print("Wprowadź poprawną liczbę.")
            time.sleep(1)
    weight += added_weight
    payload = {
        "msg_type": "MAIL_IN",
        "device_id": device_id,
        "security_code": security_code,
        "battery_level": battery,
        "weight": weight,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"Wysłano powiadomienie: {payload}")
    return weight

def simulate_package_removal(client, device_id, security_code, battery, weight):
    while True:
        show_title(device_id, security_code, battery, weight)
        prompt = 'Wprowadź wagę do usunięcia, lub symbol "*" aby usunąć całość: '
        to_remove = input(prompt)
        if to_remove.strip() == "*":
            removed_weight = weight
            weight = 0
            break
        try:
            removed_weight = float(to_remove.replace(',', '.'))
            if removed_weight <= 0:
                print("Waga musi być większa od zera.")
                time.sleep(1)
                continue
            if removed_weight > weight:
                print("Nie można usunąć więcej niż aktualna wykrywana waga!")
                time.sleep(1)
                continue
            weight -= removed_weight
            break
        except ValueError:
            print('Niepoprawna wartość. Wprowadź liczbę lub "*".')
            time.sleep(1)
    payload = {
        "msg_type": "MAIL_OUT",
        "device_id": device_id,
        "security_code": security_code,
        "battery_level": battery,
        "weight": weight,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"Wysłano powiadomienie: {payload}")
    return weight

# ----------------------------------------------------------------------------------------------------
def main():
    device_id, security_code, battery = get_device_info()
    weight = 0
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    device_id_ref = {"value": device_id}
    security_code_ref = {"value": security_code}
    battery_ref = {"value": battery}
    weight_ref = {"value": weight}
    running_flag = {"run": True}
    heartbeat_paused = {"paused": False}

    heartbeat_thread = threading.Thread(
        target=heartbeat_loop,
        args=(client, device_id_ref, security_code_ref, battery_ref, weight_ref, running_flag, heartbeat_paused),
        daemon=True
    )
    heartbeat_thread.start()

    while True:
        show_main_menu(device_id, security_code, battery, weight)
        choice = input("Twój wybór: ")
        if choice == "0":
            running_flag["run"] = False
            time.sleep(0.5)  # Dać szansę wątkowi na zakończenie
            print("Do zobaczenia!")
            break
        elif choice == "1":
            weight = simulate_package_drop(client, device_id, security_code, battery, weight)
            weight_ref["value"] = weight
            input("\nNaciśnij Enter, aby wrócić do menu...")
        elif choice == "2":
            if weight == 0:
                show_title(device_id, security_code, battery, weight)
                print("Nie można zasymulować wyciągnięcia paczki, ponieważ aktualnie wykrywana waga wynosi 0g.")
                input("\nNaciśnij Enter, aby wrócić do menu...")
            else:
                weight = simulate_package_removal(client, device_id, security_code, battery, weight)
                weight_ref["value"] = weight
                input("\nNaciśnij Enter, aby wrócić do menu...")

        elif choice == "3":
            battery = change_battery_level(device_id, security_code, battery)
            battery_ref["value"] = battery
        elif choice == "4":
            show_title(device_id, security_code, battery, weight)
            heartbeat_paused["paused"] = True
            print("Sygnał heartbeat wstrzymany.")
            input("\nNaciśnij Enter, aby wznowić sygnał heartbeat i wrócić do menu...")
            heartbeat_paused["paused"] = False
        elif choice == "5":
            weight = change_detected_weight(device_id, security_code, battery, weight)
            weight_ref["value"] = weight
        else:
            show_title(device_id, security_code, battery, weight)
            print("Niepoprawny wybór. Spróbuj ponownie.")
        
if __name__ == "__main__":
    main()

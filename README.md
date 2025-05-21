# 📬 Smart moduł do skrzynki pocztowej


## 🧩 Wymagania biznesowe

### 📦 Opis urządzenia

- Urządzenie w formie wkładki/płytki umieszczane wewnątrz skrzynki pocztowej  
- Posiada wbudowaną wagę  
- Wysyła powiadomienie do aplikacji, gdy wrzucony zostanie list lub mała paczka  
- Powiadomienia z urządzenia wysyłane są cyklicznie, dopóki aplikacja nie udzieli odpowiedzi (np. co godzinę, potem rzadziej)  
- Sprawdzanie obecności listu odbywa się na podstawie pomiaru wagi  
- *Heartbeat* - urządzenie cyklicznie przesyła sygnał do aplikacji, potwierdzając, że nadal działa. Informuje m.in. o poziomie baterii  

---

### 👤 User Stories

-  **Jako użytkownik**, chciałbym otrzymać powiadomienie za każdym razem, gdy w mojej skrzynce zostanie umieszczony list / paczka.  
-  **Jako użytkownik**, chciałbym otrzymać powiadomienie za każdym razem, gdy list / paczka zostanie odebrana.  
-  **Jako użytkownik**, chciałbym móc zdalnie sprawdzić poziom naładowania mojego urządzenia.  
-  **Jako użytkownik**, chciałbym otrzymywać powiadomienia o niskim poziomie naładowania baterii urządzenia (uwzględniając czas do jej wyczerpania).  
-  **Jako użytkownik**, chciałbym otrzymać powiadomienie w momencie, gdy urządzenie przestanie działać (np. rozładuje się bateria lub zostanie zepsute).  

---

## 📋 Wymagania projektu
Nie wszystkie są obowiązkowe, ale tym więcej tym lepsza ocena.
❌/🚧/✅

- 🚧 Kontekst Biznesowy
- ❌ C4 - Diagram Architektury - Poziom Kontekstu
- ❌ C4 - Diagram Architektury - Poziom Kontenerów
- ❌ Kalkulator kosztów Azure/AWS
- ❌ Symulator Urządzenia IoT
- ❌ Serwis MQTT Broker
- ❌ Baza Danych
- ❌ REST API
- ❌ Instrukcje Deploy'owania
- ❌ Instruckje Testowania
- ❌ Czy wszystkie wymagania biznesowe zostały pokryte?
- ❌ Czy projekt działa?
- ❌ "Infrastructure as Code"
- ❌ Kolekcja Postman
- ❌ Frontend
- ❌ Własny system rejestracji
- ❌ Możliwość zarządzania użytkownikami
- ❌ Możliwość zarządzania urządzeniami
- ❌ Czy rozwiązanie jest bezpieczne?
- ❌ Zdalna konfiguracja urządzenia

---




# 📬 Smart moduł do skrzynki pocztowej

## 📌 Business Context
W dobie coraz bardziej powszechnej cyfryzacji oraz różnorodnych, wygodnych punktów odbioru paczek, coraz rzadziej zaglądamy do prywatnej skrzynki pocztowej. Tymczasem to właśnie tam najczęściej trafiają najistotniejsze i czasowo wrażliwe przesyłki – takie jak pisma z banku, mandaty czy ważne dokumenty.

Aby rozwiązać ten problem, proponujemy Smart moduł do skrzynki pocztowej – proste urządzenie IoT w formie wkładki/płytki, które umożliwia zdalne monitorowanie zawartości skrzynki dzięki wbudowanej wadze. Gdy do skrzynki zostanie wrzucony list lub mała paczka, urządzenie automatycznie wykryje zmianę wagi i wyśle powiadomienie do użytkownika, informując go o dostawie.

Projekt wpisuje się w rozwój rozwiązań Smart Home i Smart Living, oferując wygodę i bezpieczeństwo przy minimalnej ingerencji w istniejącą infrastrukturę. Urządzenie będzie łatwe do zamontowania i nie będzie wymagało modyfikacji skrzynki pocztowej ani specjalistycznej instalacji.

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

-  **Jako użytkownik**, chciałbym mieć możliwość rejestracji i logowania się do systemu.
-  **Jako użytkownik**, chciałbym móc dodać swoje urządzenie i nadać mu nazwę.
-  **Jako użytkownik**, chciałbym móc zarządzać ustawieniami swojego konta.
-  **Jako użytkownik**, chciałbym otrzymać powiadomienie za każdym razem, gdy w mojej skrzynce zostanie umieszczony list / paczka.  
-  **Jako użytkownik**, chciałbym otrzymać powiadomienie za każdym razem, gdy list / paczka zostanie odebrana.  
-  **Jako użytkownik**, chciałbym móc zdalnie sprawdzić poziom naładowania mojego urządzenia.  
-  **Jako użytkownik**, chciałbym otrzymywać powiadomienia o niskim poziomie naładowania baterii urządzenia (uwzględniając czas do jej wyczerpania).  
-  **Jako użytkownik**, chciałbym otrzymać powiadomienie w momencie, gdy urządzenie przestanie działać (np. rozładuje się bateria lub zostanie zepsute).  

---

## 📋 Wymagania projektu

❌/🚧/✅

- ✅ Kontekst Biznesowy
- ✅ C4 - Diagram Architektury - Poziom Kontekstu
- ✅ C4 - Diagram Architektury - Poziom Kontenerów
- ✅ Kalkulator kosztów Azure/AWS
- ✅ Symulator Urządzenia IoT
- ✅ Serwis MQTT Broker
- ✅ Baza Danych
- ✅ REST API
- 🚧 Instrukcje Deploy'owania
- ❌ Instruckje Testowania
- 🚧 Czy wszystkie wymagania biznesowe zostały pokryte?
- ✅ Czy projekt działa?
- ❌ "Infrastructure as Code"
- ❌ Kolekcja Postman
- ✅ Frontend
- ✅ Własny system logowania i rejestracji
- ✅ Możliwość zarządzania użytkownikami
- ✅ Możliwość zarządzania urządzeniami
- 🚧 Czy rozwiązanie jest bezpieczne?
- ❌ Zdalna konfiguracja urządzenia

---

### 🔢 Skalowanie – Szacunki
| Liczba użytkowników | Koszt minimalny        | Koszt rozsądny           |
|---------------------|------------------------|-------------------------|
| 100 użytkowników    | ~$90–110/miesiąc       | ~$130–150/miesiąc       |
| 1000 użytkowników   | ~$150–200/miesiąc      | ~$250–300/miesiąc       |



# Oficjalny obrazu Pythona
FROM python:3.12

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj requirements i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu projektu
COPY . .
RUN python manage.py collectstatic --noinput
# Ustaw zmienne środowiskowe (możesz też je przekazać przez Azure)
ENV PYTHONUNBUFFERED=1

# Port na którym uruchamiasz Django (Azure nasłuchuje na 8000 domyślnie)
EXPOSE 8000

# Uruchom serwer produkcyjny (np. gunicorn)
CMD ["gunicorn", "smartmailbox.wsgi:application", "--bind", "0.0.0.0:8000"]

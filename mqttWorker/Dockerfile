FROM python:3.12-slim
WORKDIR /app
COPY mqtt_worker.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "mqtt_worker.py"]
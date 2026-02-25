FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
# Explicitly tell Gunicorn where the app is
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app", "--workers", "4", "--log-level", "debug"]

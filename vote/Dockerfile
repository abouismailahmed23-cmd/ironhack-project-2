FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
# Gunicorn handles form data much more reliably through Ingress
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--workers", "4", "--keep-alive", "0"]

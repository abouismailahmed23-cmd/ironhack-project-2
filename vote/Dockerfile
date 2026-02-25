FROM python:3.11-slim
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy code
COPY . .
EXPOSE 80
# Gunicorn is required for Ingress to handle form data (POST) correctly
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--workers", "4", "--keep-alive", "0"]

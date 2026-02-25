FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
# Simplified CMD
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]

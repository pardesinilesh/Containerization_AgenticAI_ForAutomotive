# Dockerfile for API service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

ENV PYTHONUNBUFFERED=1
ENV WORKERS=4

EXPOSE 8080

CMD ["uvicorn", "agent.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]

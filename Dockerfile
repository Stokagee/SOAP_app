FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for lxml and psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose SOAP service port
EXPOSE 8000

# Run the SOAP service
CMD ["python", "-m", "app.main"]

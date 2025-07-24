FROM python:3.12-slim

WORKDIR /app

# Update package lists and install system dependencies with retry logic
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libc6-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

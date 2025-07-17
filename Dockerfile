# Single-stage build
FROM python:3.10-slim

WORKDIR /app

# Install all dependencies (build + runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=1 \
    UVICORN_TIMEOUT=60 \
    UVICORN_LIMIT_CONCURRENCY=50



EXPOSE 5551


CMD ["python","main.py"]
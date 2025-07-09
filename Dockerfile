# # Multi-stage build to reduce final image size
# FROM python:3.10-slim as builder

# # Install build dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     git \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --user -r requirements.txt

# # Final stage
# FROM python:3.10-slim
# WORKDIR /app

# # Runtime dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     ffmpeg \
#     libsndfile1 \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Copy only necessary files
# COPY --from=builder /root/.local /root/.local
# COPY . .

# # Environment variables
# ENV PATH=/root/.local/bin:$PATH \
#     PYTHONPATH=/app \
#     PYTHONUNBUFFERED=1 \
#     UVICORN_WORKERS=1 \
#     UVICORN_TIMEOUT=60 \
#     UVICORN_LIMIT_CONCURRENCY=50

# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
#     CMD curl -f http://localhost:5551/health || exit 1

# EXPOSE 5551

# # Run as non-root user
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# CMD ["python","consumer.py"]

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

# # Run as non-root user
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

CMD ["python","consumer.py"]
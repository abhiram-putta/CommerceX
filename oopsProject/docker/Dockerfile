# Multi-stage Dockerfile for sMart Backend

# Stage 1: Base image with dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Development image
FROM base as development

# Copy requirements
COPY requirements/ /app/requirements/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt && \
    pip install -r requirements/ml.txt && \
    pip install -r requirements/dev.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 8000

# Run development server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production image
FROM base as production

# Copy requirements
COPY requirements/ /app/requirements/

# Install Python dependencies (without dev dependencies)
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt && \
    pip install -r requirements/ml.txt

# Copy application code
COPY app/ /app/app/
COPY migrations/ /app/migrations/
COPY alembic.ini /app/
COPY scripts/ /app/scripts/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

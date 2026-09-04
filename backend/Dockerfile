FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    WEB_CONCURRENCY=1

WORKDIR /workspace

# Install system dependencies required by ReportLab/PyCairo, PostgreSQL, PyTorch, and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    libcairo2 \
    libcairo2-dev \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Keep runtime-created files writable without running the server as root.
RUN useradd --create-home --shell /usr/sbin/nologin appuser && \
    mkdir -p /workspace/uploads && \
    chown -R appuser:appuser /workspace

USER appuser

# Expose application port
EXPOSE 8000

# Allow the platform to override PORT and WEB_CONCURRENCY at runtime.
CMD ["sh", "-c", "exec gunicorn app.main:app --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY} --worker-class uvicorn.workers.UvicornWorker --timeout 120 --access-logfile - --error-logfile -"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health', timeout=5)"
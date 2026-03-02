FROM python:3.11-slim

LABEL maintainer="Wealthsimple AI Builders"
LABEL description="AI-Native Regulatory Compliance Monitoring System"

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ backend/
COPY data/ data/
COPY eval/ eval/
COPY frontend/ frontend/
COPY tests/ tests/

# Create data directory for SQLite + LLM cache
RUN mkdir -p /app/data

# Default port (Railway/Render inject PORT env var automatically)
ENV PORT=8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/api/health')" || exit 1

# Production: gunicorn with uvicorn workers
CMD gunicorn backend.server:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:${PORT} \
    --timeout 120 \
    --access-logfile -

FROM python:3.12-slim

WORKDIR /app

# Install deps first so this layer is cached across code-only changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# app/data is where MovieLens CSVs / build artifacts live. It's intentionally
# NOT baked into the image (see .dockerignore) — mount it as a volume so you
# can drop your real dataset in without rebuilding. The app boots fine even
# if it's empty; /api/v1/health reports "degraded" until artifacts exist.
RUN mkdir -p app/data/raw app/data/processed app/data/artifacts app/data/tmdb_cache

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','8000'); sys.exit(0 if urllib.request.urlopen(f'http://localhost:{p}/api/v1/health', timeout=3).status == 200 else 1)"

# Shell form (not exec-form JSON array) so $PORT actually expands. Railway
# injects PORT dynamically; locally/in docker-compose it's unset, so this
# falls back to 8000 to match docker-compose.yml's port mapping exactly.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

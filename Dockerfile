# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=healmymind.settings \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and create superuser
RUN python manage.py migrate

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1

# Start Gunicorn
CMD gunicorn healmymind.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keep-alive 5 --log-level info --access-logfile - --error-logfile -

# Create docker-compose.yml for local development
RUN echo "version: '3.8'\n\
\n\
services:\n\
  web:\n\
    build: .\n\
    command: python manage.py runserver 0.0.0.0:8000\n\
    volumes:\n\
      - .:/app\n\
    ports:\n\
      - '8000:8000'\n\
    environment:\n\
      - DEBUG=1\n\
      - DJANGO_SETTINGS_MODULE=healmymind.settings\n\
    depends_on:\n\
      - mongodb\n\
      - redis\n\
\n\
  mongodb:\n\
    image: mongo:latest\n\
    ports:\n\
      - '27017:27017'\n\
    volumes:\n\
      - mongodb_data:/data/db\n\
\n\
  redis:\n\
    image: redis:alpine\n\
    ports:\n\
      - '6379:6379'\n\
\n\
  celery:\n\
    build: .\n\
    command: celery -A healmymind worker -l info\n\
    volumes:\n\
      - .:/app\n\
    depends_on:\n\
      - redis\n\
      - mongodb\n\
\n\
  celery-beat:\n\
    build: .\n\
    command: celery -A healmymind beat -l info\n\
    volumes:\n\
      - .:/app\n\
    depends_on:\n\
      - redis\n\
      - mongodb\n\
\n\
volumes:\n\
  mongodb_data:\n" > docker-compose.yml

# Create .dockerignore
RUN echo "*.pyc\n\
__pycache__\n\
*.pyo\n\
*.pyd\n\
.Python\n\
env\n\
pip-log.txt\n\
pip-delete-this-directory.txt\n\
.tox\n\
.coverage\n\
.coverage.*\n\
.cache\n\
nosetests.xml\n\
coverage.xml\n\
*.cover\n\
*.log\n\
.pytest_cache\n\
.env\n\
.venv\n\
venv/\n\
ENV/\n\
.git\n\
.gitignore\n\
.idea\n\
.vscode\n\
*.swp\n\
*.swo\n\
*~\n\
staticfiles\n\
media\n\
node_modules\n\
dist\n\
build\n\
*.egg-info\n" > .dockerignore

# Create production.Dockerfile for production deployment
RUN echo "FROM python:3.11-slim\n\
\n\
ENV PYTHONDONTWRITEBYTECODE=1 \\\n\
    PYTHONUNBUFFERED=1 \\\n\
    DJANGO_SETTINGS_MODULE=healmymind.settings \\\n\
    PORT=8000\n\
\n\
WORKDIR /app\n\
\n\
RUN apt-get update && apt-get install -y --no-install-recommends \\\n\
    build-essential \\\n\
    libpq-dev \\\n\
    && rm -rf /var/lib/apt/lists/*\n\
\n\
COPY requirements.txt .\n\
RUN pip install --no-cache-dir -r requirements.txt\n\
\n\
COPY . .\n\
\n\
RUN useradd -m appuser && chown -R appuser:appuser /app\n\
USER appuser\n\
\n\
RUN python manage.py collectstatic --noinput\n\
RUN python manage.py migrate\n\
\n\
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n\
    CMD curl -f http://localhost:$PORT/health/ || exit 1\n\
\n\
CMD gunicorn healmymind.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keep-alive 5 --log-level info --access-logfile - --error-logfile -\n" > production.Dockerfile

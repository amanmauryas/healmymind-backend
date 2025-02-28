# healmymind Backend Deployment Guide

This guide covers the setup and deployment of the healmymind backend service.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB
- Redis
- Kubernetes (for production deployment)
- Node.js 18+ (for frontend integration)

## Local Development

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate     # Unix/MacOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
DEBUG=True
SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/healmymind
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGIN_WHITELIST=http://localhost:3000
```

4. Run development server:
```bash
./scripts/manage.sh run
```

## Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access services:
- Django API: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379
- Flower (Celery monitoring): http://localhost:5555

## Kubernetes Deployment

1. Configure Kubernetes secrets:
```bash
kubectl create secret generic healmymind-secrets \
  --from-literal=django-secret-key=$(./scripts/manage.sh secret) \
  --from-literal=mongodb-uri=mongodb+srv://your-mongodb-uri \
  --from-literal=redis-url=redis://your-redis-url
```

2. Deploy to Kubernetes:
```bash
kubectl apply -f k8s/deployment.yaml
```

3. Verify deployment:
```bash
kubectl get pods -n healmymind
kubectl get services -n healmymind
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DJANGO_SETTINGS_MODULE | Django settings module | Yes | healmymind.settings |
| SECRET_KEY | Django secret key | Yes | None |
| MONGODB_URI | MongoDB connection URI | Yes | None |
| DEBUG | Debug mode | No | False |
| ALLOWED_HOSTS | Allowed hosts | No | [] |
| CORS_ORIGIN_WHITELIST | CORS allowed origins | No | [] |
| CELERY_BROKER_URL | Redis URL for Celery | Yes | None |

## Database Setup

1. MongoDB Setup:
```bash
# Local development
mongod --dbpath /path/to/data/db

# Production (MongoDB Atlas)
# Use the connection string from MongoDB Atlas
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

## Monitoring

1. Application Monitoring:
- Health check endpoint: `/health/`
- Metrics endpoint: `/metrics/`
- Admin interface: `/admin/`

2. Celery Monitoring:
- Flower dashboard: http://localhost:5555

3. Logging:
- Application logs: `logs/app.log`
- Celery logs: `logs/celery.log`
- Nginx logs: `logs/nginx-access.log`, `logs/nginx-error.log`

## Troubleshooting

### Common Issues

1. Database Connection Issues:
```bash
# Check MongoDB connection
mongosh mongodb://localhost:27017/healmymind

# Check MongoDB logs
docker-compose logs mongodb
```

2. Celery Issues:
```bash
# Check Celery worker status
celery -A healmymind status

# Check Celery logs
docker-compose logs celery
```

3. Static Files Issues:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check static files directory
ls staticfiles/
```

### Health Checks

1. Backend Health:
```bash
curl http://localhost:8000/health/
```

2. Services Health:
```bash
# Check all services
./scripts/manage.sh status

# Check specific service
docker-compose ps
```

### Backup and Restore

1. Create backup:
```bash
./scripts/manage.sh backup
```

2. Restore from backup:
```bash
./scripts/manage.sh restore backups/backup_20240228_120000
```

### Security

1. SSL/TLS Configuration:
- Production deployments should use HTTPS
- Configure SSL certificate in Nginx or use cloud provider's SSL termination
- Enable HSTS in Django settings

2. Security Headers:
- Configured in Nginx and Django middleware
- Includes CSP, HSTS, XSS protection, etc.

3. Rate Limiting:
- API rate limiting configured in Django settings
- Additional rate limiting at Nginx level

### Performance Optimization

1. Caching:
- Redis caching configured for session and general caching
- Cache timeout settings in Django settings

2. Database:
- MongoDB indexes created for frequently accessed fields
- Query optimization in Django ORM

3. Static Files:
- Served through Nginx
- Configured with proper caching headers

### Scaling

1. Horizontal Scaling:
- Kubernetes HPA configured for auto-scaling
- Stateless application design
- Session persistence through Redis

2. Vertical Scaling:
- Resource limits configured in Kubernetes
- MongoDB and Redis resource allocation

### Maintenance

1. Regular Tasks:
```bash
# Database backup
./scripts/manage.sh backup

# Log rotation
logrotate /etc/logrotate.d/healmymind

# Clear cache
python manage.py clearcache
```

2. Updates:
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Apply migrations
python manage.py migrate
```

3. Monitoring:
- Set up monitoring alerts
- Configure log aggregation
- Monitor resource usage

For additional support or questions, please refer to the project documentation or contact the development team.

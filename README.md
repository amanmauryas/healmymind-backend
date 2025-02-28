# healmymind Backend

The backend service for healmymind.ai, a mental health screening and support platform.

## Features

- 🔐 User Authentication & Authorization
- 🧠 Mental Health Tests & Analysis
- 📝 Blog System
- 💬 AI-Powered Chat Support
- 📊 Analytics & Reporting
- 🔄 Real-time WebSocket Communication
- 📱 RESTful API
- 🗄️ MongoDB Integration
- 📨 Celery Task Queue
- 🚀 Scalable Architecture

## Tech Stack

- **Framework**: Django + Django REST Framework
- **Database**: MongoDB (via Djongo)
- **Cache & Message Broker**: Redis
- **Task Queue**: Celery
- **Web Server**: Nginx + Gunicorn
- **API Documentation**: Swagger/OpenAPI
- **Testing**: pytest
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healmymind.git
cd healmymind/backend
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Start the development server:
```bash
./scripts/manage.sh run
```

4. Visit:
- API: http://localhost:8000/api/
- Admin Interface: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/docs/

## Project Structure

```
backend/
├── healmymind/          # Main project settings
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   ├── wsgi.py         # WSGI configuration
│   └── asgi.py        # ASGI configuration
├── users/              # User management app
├── tests/             # Mental health tests app
├── blog/             # Blog system app
├── chat/            # Chat support app
├── scripts/        # Management scripts
├── k8s/           # Kubernetes configurations
└── requirements.txt  # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/users/register/` - Register new user

### Users
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/update/` - Update profile
- `POST /api/users/change-password/` - Change password

### Tests
- `GET /api/tests/` - List available tests
- `GET /api/tests/<id>/` - Get test details
- `POST /api/tests/<id>/submit/` - Submit test answers

### Blog
- `GET /api/blog/posts/` - List blog posts
- `GET /api/blog/posts/<slug>/` - Get post details
- `POST /api/blog/posts/<slug>/comments/` - Add comment

### Chat
- `GET /api/chat/conversations/` - List conversations
- `POST /api/chat/conversations/create/` - Start new conversation
- `POST /api/chat/conversations/<id>/send/` - Send message

## Development

### Virtual Environment

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate     # Unix/MacOS
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

### Database Setup

1. Install MongoDB:
```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community

# Ubuntu
sudo apt-get install mongodb
```

2. Run migrations:
```bash
python manage.py migrate
```

### Running Tests

```bash
# Run all tests
./scripts/manage.sh test

# Run specific test
python manage.py test tests.test_models
```

### Code Style

We use Black for code formatting and flake8 for linting:
```bash
# Format code
black .

# Check style
flake8
```

## Docker Development

1. Build and run services:
```bash
docker-compose up --build
```

2. Run commands in container:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Documentation

- API Documentation: `/api/docs/`
- Admin Guide: `/admin/docs/`
- User Guide: `/docs/user-guide/`

## Monitoring

- Application Health: `/health/`
- Metrics: `/metrics/`
- Celery Monitoring: `:5555` (Flower)

## Support

- GitHub Issues: [Report Bug](https://github.com/yourusername/healmymind/issues)
- Email: support@healmymindai.com
- Discord: [Join Community](https://discord.gg/healmymind)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [MongoDB](https://www.mongodb.com/)
- [Celery](https://docs.celeryproject.org/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

## Security

For security issues, please email security@healmymindai.com

## Roadmap

- [ ] Enhanced AI Analysis
- [ ] Real-time Chat Translation
- [ ] Mobile App Integration
- [ ] Advanced Analytics Dashboard
- [ ] Integration with External Health Providers

## Authors

- Your Name - Initial work - [GitHub](https://github.com/yourusername)

## Status

[![Build Status](https://github.com/yourusername/healmymind/workflows/CI/badge.svg)](https://github.com/yourusername/healmymind/actions)
[![Coverage Status](https://coveralls.io/repos/github/yourusername/healmymind/badge.svg?branch=main)](https://coveralls.io/github/yourusername/healmymind?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

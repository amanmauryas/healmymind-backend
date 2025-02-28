# healmymind Backend Quick Start Guide

This guide will help you get started with the healmymind backend development environment.

## Prerequisites

### Windows
- [Python 3.11+](https://www.python.org/downloads/)
- [Git for Windows](https://gitforwindows.org/)
- [MongoDB Community Edition](https://www.mongodb.com/try/download/community)
- [Redis (via WSL)](https://redis.io/docs/getting-started/installation/install-redis-on-windows/)
- [Node.js 18+](https://nodejs.org/) (for frontend integration)

### macOS
```bash
# Using Homebrew
brew install python mongodb/brew/mongodb-community redis node
```

### Linux (Ubuntu/Debian)
```bash
# Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv

# Install MongoDB
sudo apt install mongodb

# Install Redis
sudo apt install redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

## Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healmymind.git
cd healmymind/backend
```

2. Run the setup script for your platform:

### Windows
```batch
# Using Command Prompt
run.bat init

# Using PowerShell
.\run.ps1 init
```

### Unix/Linux/macOS
```bash
chmod +x run.sh
./run.sh init
```

This will:
- Create a virtual environment
- Install dependencies
- Set up the database
- Create necessary directories
- Generate configuration files
- Create a superuser

## Running the Development Server

### Windows
```batch
# Command Prompt
run.bat manage runserver

# PowerShell
.\run.ps1 manage runserver
```

### Unix/Linux/macOS
```bash
./run.sh manage runserver
```

The server will be available at http://localhost:8000

## Common Tasks

### Running Tests
```bash
# Run all tests
./run.sh test

# Run with coverage
./run.sh test --coverage

# Run specific tests
./run.sh test tests.test_models
```

### Database Operations
```bash
# Run migrations
./run.sh db migrate

# Create database backup
./run.sh db backup

# Restore from backup
./run.sh db restore backups/backup_20240228_120000
```

### Deployment
```bash
# Build Docker image
./run.sh deploy build

# Deploy to staging
./run.sh deploy staging

# Deploy to production
./run.sh deploy production
```

### Monitoring
```bash
# Check system health
./run.sh monitor health

# View logs
./run.sh monitor logs

# Generate status report
./run.sh monitor report
```

## Project Structure

```
backend/
├── healmymind/          # Main project settings
├── users/                # User management
├── tests/                # Mental health tests
├── blog/                 # Blog system
├── chat/                 # Chat support
├── scripts/             # Management scripts
└── requirements.txt     # Python dependencies
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Environment Variables

Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

Key variables to configure:
- `DEBUG`: Set to False in production
- `SECRET_KEY`: Django secret key
- `MONGODB_URI`: MongoDB connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ORIGIN_WHITELIST`: Allowed CORS origins

## Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and run tests:
```bash
./run.sh test
```

3. Commit your changes:
```bash
git add .
git commit -m "Add your feature"
```

4. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Troubleshooting

### Database Issues
```bash
# Check MongoDB status
./run.sh monitor health

# Reset database
./run.sh db reset
```

### Server Issues
```bash
# Clear cache
./run.sh manage clearcache

# Restart server
./run.sh manage runserver
```

### Dependencies Issues
```bash
# Update dependencies
./run.sh manage update-deps

# Clear virtual environment
rm -rf venv
./run.sh init
```

## Getting Help

- Check the full documentation in `README.md`
- View deployment guide in `DEPLOYMENT.md`
- Run `./run.sh help` for command help
- Contact the development team

## Next Steps

1. Review the API documentation
2. Explore the test suite
3. Set up your IDE (recommended: VS Code with Python extension)
4. Join the development chat

For more detailed information, see the full documentation in `README.md`.

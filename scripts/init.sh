#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Make all scripts executable
print_message $YELLOW "Making scripts executable..."
chmod +x scripts/*.sh

# Create necessary directories
print_message $YELLOW "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p backups
mkdir -p reports

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_message $YELLOW "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_message $YELLOW "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_message $YELLOW "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_message $YELLOW "Creating .env file from example..."
    cp .env.example .env
    
    # Generate Django secret key
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    print_message $YELLOW "Initializing git repository..."
    git init
    
    # Add initial commit
    git add .
    git commit -m "Initial commit"
fi

# Setup git hooks
print_message $YELLOW "Setting up git hooks..."
mkdir -p .git/hooks

# Pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
source venv/bin/activate

# Run tests
./scripts/test.sh
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix the issues and try again."
    exit 1
fi

# Run linting
./scripts/test.sh lint
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix the issues and try again."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-commit

# Pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
source venv/bin/activate

# Run all checks
./scripts/test.sh all
if [ $? -ne 0 ]; then
    echo "Checks failed. Please fix the issues and try again."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-push

# Run initial database setup
print_message $YELLOW "Running initial database setup..."
./scripts/db.sh migrate
./scripts/db.sh seed

# Collect static files
print_message $YELLOW "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_message $YELLOW "Checking for superuser..."
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.filter(is_superuser=True).exists())"; then
    print_message $YELLOW "Creating superuser..."
    python manage.py createsuperuser
fi

# Final instructions
print_message $GREEN "\nProject initialization complete! Here's what you can do next:"
print_message $YELLOW "1. Review and update the .env file with your configuration"
print_message $YELLOW "2. Start the development server: ./scripts/manage.sh run"
print_message $YELLOW "3. Run tests: ./scripts/test.sh"
print_message $YELLOW "4. Monitor the application: ./scripts/monitor.sh"
print_message $YELLOW "5. Deploy the application: ./scripts/deploy.sh"

print_message $GREEN "\nAvailable scripts:"
print_message $YELLOW "- manage.sh: General management commands"
print_message $YELLOW "- db.sh: Database management commands"
print_message $YELLOW "- test.sh: Testing and code quality commands"
print_message $YELLOW "- deploy.sh: Deployment commands"
print_message $YELLOW "- monitor.sh: Monitoring and maintenance commands"

print_message $GREEN "\nHappy coding! 🚀"

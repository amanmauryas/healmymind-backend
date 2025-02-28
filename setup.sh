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

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_message $RED "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_message $RED "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Check if virtualenv is installed
if ! command -v virtualenv &> /dev/null; then
    print_message $YELLOW "Installing virtualenv..."
    pip3 install virtualenv
fi

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

# Create necessary directories
print_message $YELLOW "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p backups

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_message $YELLOW "Creating .env file from example..."
    cp .env.example .env
    
    # Generate Django secret key
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
fi

# Check if MongoDB is installed and running
print_message $YELLOW "Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    print_message $RED "MongoDB is not installed. Please install MongoDB and try again."
    print_message $YELLOW "Visit: https://docs.mongodb.com/manual/installation/"
    exit 1
fi

# Check if Redis is installed and running
print_message $YELLOW "Checking Redis..."
if ! command -v redis-cli &> /dev/null; then
    print_message $RED "Redis is not installed. Please install Redis and try again."
    print_message $YELLOW "Visit: https://redis.io/topics/quickstart"
    exit 1
fi

# Run database migrations
print_message $YELLOW "Running database migrations..."
python manage.py migrate

# Collect static files
print_message $YELLOW "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_message $YELLOW "Checking for superuser..."
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.filter(is_superuser=True).exists())"; then
    print_message $YELLOW "Creating superuser..."
    python manage.py createsuperuser
fi

# Make manage.sh executable
chmod +x scripts/manage.sh

# Setup git hooks
print_message $YELLOW "Setting up git hooks..."
if [ -d ".git" ]; then
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
source venv/bin/activate
python manage.py check
if [ $? -ne 0 ]; then
    echo "Django check failed. Please fix the issues and try again."
    exit 1
fi
EOF
    chmod +x .git/hooks/pre-commit
    
    # Pre-push hook
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
source venv/bin/activate
python manage.py test
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix the issues and try again."
    exit 1
fi
EOF
    chmod +x .git/hooks/pre-push
fi

# Final instructions
print_message $GREEN "\nSetup complete! Here's what you need to do next:"
print_message $YELLOW "1. Review and update the .env file with your configuration"
print_message $YELLOW "2. Start the development server: ./scripts/manage.sh run"
print_message $YELLOW "3. Visit http://localhost:8000/admin to access the admin interface"
print_message $YELLOW "4. Run tests with: ./scripts/manage.sh test"
print_message $YELLOW "5. For deployment instructions, see DEPLOYMENT.md"

print_message $GREEN "\nHappy coding! 🚀"

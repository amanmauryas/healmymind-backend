#!/bin/bash

# Set environment variables
export DJANGO_SETTINGS_MODULE=healmymind.settings
export PYTHONPATH=$PYTHONPATH:$(pwd)

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check dependencies
check_dependencies() {
    print_message $YELLOW "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists kubectl; then
        missing_deps+=("kubectl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_message $RED "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi
    
    print_message $GREEN "All dependencies are installed."
}

# Function to setup development environment
setup_dev() {
    print_message $YELLOW "Setting up development environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run migrations
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(User.objects.filter(is_superuser=True).exists())"; then
        print_message $YELLOW "Creating superuser..."
        python manage.py createsuperuser
    fi
    
    print_message $GREEN "Development environment setup complete."
}

# Function to run development server
run_dev() {
    print_message $YELLOW "Starting development server..."
    docker-compose up
}

# Function to run tests
run_tests() {
    print_message $YELLOW "Running tests..."
    python manage.py test
}

# Function to build Docker image
build_docker() {
    print_message $YELLOW "Building Docker image..."
    docker build -t healmymind/web:latest .
}

# Function to deploy to Kubernetes
deploy_k8s() {
    print_message $YELLOW "Deploying to Kubernetes..."
    
    # Check if kubectl is configured
    if ! kubectl cluster-info &> /dev/null; then
        print_message $RED "kubectl is not configured properly"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace healmymind --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kubernetes configurations
    kubectl apply -f k8s/deployment.yaml
    
    print_message $GREEN "Deployment complete."
}

# Function to collect static files
collect_static() {
    print_message $YELLOW "Collecting static files..."
    python manage.py collectstatic --noinput
}

# Function to create database backup
backup_db() {
    print_message $YELLOW "Creating database backup..."
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="backups"
    
    mkdir -p $backup_dir
    mongodump --uri "$MONGODB_URI" --out "$backup_dir/backup_$timestamp"
    
    print_message $GREEN "Backup created at $backup_dir/backup_$timestamp"
}

# Function to restore database from backup
restore_db() {
    if [ -z "$1" ]; then
        print_message $RED "Please specify backup directory"
        exit 1
    fi
    
    print_message $YELLOW "Restoring database from backup..."
    mongorestore --uri "$MONGODB_URI" "$1"
    
    print_message $GREEN "Database restored from backup"
}

# Function to generate secret key
generate_secret() {
    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
}

# Main script logic
case "$1" in
    "setup")
        check_dependencies
        setup_dev
        ;;
    "run")
        run_dev
        ;;
    "test")
        run_tests
        ;;
    "build")
        build_docker
        ;;
    "deploy")
        deploy_k8s
        ;;
    "static")
        collect_static
        ;;
    "backup")
        backup_db
        ;;
    "restore")
        restore_db "$2"
        ;;
    "secret")
        generate_secret
        ;;
    *)
        print_message $YELLOW "Usage: $0 {setup|run|test|build|deploy|static|backup|restore|secret}"
        exit 1
        ;;
esac

exit 0

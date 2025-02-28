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

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_deps+=("kubectl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_message $RED "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi
}

# Function to build Docker image
build_image() {
    local tag=${1:-latest}
    print_message $YELLOW "Building Docker image with tag: $tag"
    
    docker build -t healmymind/web:$tag -f Dockerfile .
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "Docker image built successfully"
    else
        print_message $RED "Docker image build failed"
        exit 1
    fi
}

# Function to push Docker image
push_image() {
    local tag=${1:-latest}
    print_message $YELLOW "Pushing Docker image with tag: $tag"
    
    docker push healmymind/web:$tag
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "Docker image pushed successfully"
    else
        print_message $RED "Docker image push failed"
        exit 1
    fi
}

# Function to deploy to Kubernetes
deploy_k8s() {
    local env=${1:-staging}
    print_message $YELLOW "Deploying to $env environment"
    
    # Check if kubectl is configured
    if ! kubectl cluster-info &> /dev/null; then
        print_message $RED "kubectl is not configured properly"
        exit 1
    fi
    
    # Apply Kubernetes configurations
    kubectl apply -f k8s/deployment.yaml
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "Deployment successful"
    else
        print_message $RED "Deployment failed"
        exit 1
    fi
}

# Function to rollback deployment
rollback() {
    print_message $YELLOW "Rolling back deployment..."
    
    kubectl rollout undo deployment/healmymind-web -n healmymind
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "Rollback successful"
    else
        print_message $RED "Rollback failed"
        exit 1
    fi
}

# Function to check deployment status
check_status() {
    print_message $YELLOW "Checking deployment status..."
    
    kubectl get pods -n healmymind
    kubectl get services -n healmymind
    kubectl get deployments -n healmymind
}

# Function to view logs
view_logs() {
    local pod_name=$(kubectl get pods -n healmymind -l app=healmymind-web -o jsonpath="{.items[0].metadata.name}")
    
    if [ -z "$pod_name" ]; then
        print_message $RED "No pods found"
        exit 1
    fi
    
    kubectl logs -f $pod_name -n healmymind
}

# Function to setup SSL
setup_ssl() {
    print_message $YELLOW "Setting up SSL certificates..."
    
    # Check if cert-manager is installed
    if ! kubectl get namespace cert-manager &> /dev/null; then
        print_message $YELLOW "Installing cert-manager..."
        kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.7.1/cert-manager.yaml
    fi
    
    # Apply SSL configuration
    kubectl apply -f k8s/ssl-config.yaml
    
    print_message $GREEN "SSL setup completed"
}

# Function to setup monitoring
setup_monitoring() {
    print_message $YELLOW "Setting up monitoring..."
    
    # Install Prometheus and Grafana
    kubectl apply -f k8s/monitoring/
    
    print_message $GREEN "Monitoring setup completed"
}

# Function to run database migrations
run_migrations() {
    print_message $YELLOW "Running database migrations..."
    
    local pod_name=$(kubectl get pods -n healmymind -l app=healmymind-web -o jsonpath="{.items[0].metadata.name}")
    
    if [ -z "$pod_name" ]; then
        print_message $RED "No pods found"
        exit 1
    fi
    
    kubectl exec -it $pod_name -n healmymind -- python manage.py migrate
}

# Function to collect static files
collect_static() {
    print_message $YELLOW "Collecting static files..."
    
    local pod_name=$(kubectl get pods -n healmymind -l app=healmymind-web -o jsonpath="{.items[0].metadata.name}")
    
    if [ -z "$pod_name" ]; then
        print_message $RED "No pods found"
        exit 1
    fi
    
    kubectl exec -it $pod_name -n healmymind -- python manage.py collectstatic --noinput
}

# Function to show help message
show_help() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  build [tag]        Build Docker image"
    echo "  push [tag]         Push Docker image"
    echo "  deploy [env]       Deploy to Kubernetes"
    echo "  rollback          Rollback deployment"
    echo "  status            Check deployment status"
    echo "  logs              View application logs"
    echo "  ssl               Setup SSL certificates"
    echo "  monitoring        Setup monitoring"
    echo "  migrate           Run database migrations"
    echo "  static            Collect static files"
    echo "  help              Show this help message"
    echo
    echo "Options:"
    echo "  --verbose         Show verbose output"
    echo "  --dry-run         Show what would be done"
}

# Check dependencies
check_dependencies

# Parse command line arguments
case "$1" in
    "build")
        build_image "$2"
        ;;
    "push")
        push_image "$2"
        ;;
    "deploy")
        deploy_k8s "$2"
        ;;
    "rollback")
        rollback
        ;;
    "status")
        check_status
        ;;
    "logs")
        view_logs
        ;;
    "ssl")
        setup_ssl
        ;;
    "monitoring")
        setup_monitoring
        ;;
    "migrate")
        run_migrations
        ;;
    "static")
        collect_static
        ;;
    "help"|"")
        show_help
        ;;
    *)
        print_message $RED "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0

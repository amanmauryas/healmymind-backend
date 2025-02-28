#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if ! command -v mongod &> /dev/null; then
        missing_deps+=("mongodb")
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        missing_deps+=("redis")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_message $RED "Missing dependencies: ${missing_deps[*]}"
        print_message $YELLOW "Please install the required dependencies and try again."
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ ! -d "venv" ]; then
        print_message $YELLOW "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    print_message $YELLOW "Activating virtual environment..."
    source venv/bin/activate
    
    if [ ! -f "venv/updated" ] || [ requirements.txt -nt venv/updated ]; then
        print_message $YELLOW "Installing/updating dependencies..."
        pip install -r requirements.txt
        touch venv/updated
    fi
}

# Function to show help
show_help() {
    print_message $CYAN "\nhealmymind Backend Management Script"
    print_message $CYAN "================================\n"
    
    echo "Usage: ./run.sh <command> [arguments]"
    echo
    print_message $YELLOW "Commands:"
    echo "  init     - Initialize the project"
    echo "  manage   - Run Django management commands"
    echo "  db       - Database management"
    echo "  test     - Run tests and code quality checks"
    echo "  deploy   - Deployment commands"
    echo "  monitor  - Monitoring and maintenance"
    echo
    print_message $YELLOW "Examples:"
    echo "  ./run.sh init"
    echo "  ./run.sh test --coverage"
    echo "  ./run.sh manage runserver"
    echo "  ./run.sh db migrate"
}

# Make scripts executable if they aren't already
chmod_if_needed() {
    if [ ! -x "$1" ]; then
        chmod +x "$1"
    fi
}

# Ensure all scripts are executable
ensure_executable_scripts() {
    chmod_if_needed "scripts/init.sh"
    chmod_if_needed "scripts/manage.sh"
    chmod_if_needed "scripts/db.sh"
    chmod_if_needed "scripts/test.sh"
    chmod_if_needed "scripts/deploy.sh"
    chmod_if_needed "scripts/monitor.sh"
    chmod_if_needed "setup.sh"
}

# Main script logic
main() {
    # Get command from arguments
    local command=$1
    shift
    local args=("$@")
    
    # Show help if no command provided
    if [ -z "$command" ]; then
        show_help
        exit 0
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Make sure scripts are executable
    ensure_executable_scripts
    
    # Activate virtual environment
    activate_venv
    
    # Execute command
    case "$command" in
        "init")
            print_message $YELLOW "Initializing project..."
            ./scripts/init.sh "${args[@]}"
            ;;
        "manage")
            print_message $YELLOW "Running management command..."
            ./scripts/manage.sh "${args[@]}"
            ;;
        "db")
            print_message $YELLOW "Running database command..."
            ./scripts/db.sh "${args[@]}"
            ;;
        "test")
            print_message $YELLOW "Running tests..."
            ./scripts/test.sh "${args[@]}"
            ;;
        "deploy")
            print_message $YELLOW "Running deployment command..."
            ./scripts/deploy.sh "${args[@]}"
            ;;
        "monitor")
            print_message $YELLOW "Running monitoring command..."
            ./scripts/monitor.sh "${args[@]}"
            ;;
        *)
            print_message $RED "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
    
    # Check if command was successful
    if [ $? -ne 0 ]; then
        print_message $RED "Command failed with exit code $?"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"

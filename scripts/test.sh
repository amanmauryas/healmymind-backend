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
    
    if ! command -v pytest &> /dev/null; then
        missing_deps+=("pytest")
    fi
    
    if ! command -v coverage &> /dev/null; then
        missing_deps+=("coverage")
    fi
    
    if ! command -v black &> /dev/null; then
        missing_deps+=("black")
    fi
    
    if ! command -v flake8 &> /dev/null; then
        missing_deps+=("flake8")
    fi
    
    if ! command -v isort &> /dev/null; then
        missing_deps+=("isort")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_message $YELLOW "Installing missing dependencies: ${missing_deps[*]}"
        pip install "${missing_deps[@]}"
    fi
}

# Function to run tests
run_tests() {
    print_message $YELLOW "Running tests..."
    
    if [ "$1" = "--coverage" ]; then
        coverage run -m pytest
        coverage report
        coverage html
        print_message $GREEN "Coverage report generated in htmlcov/index.html"
    else
        pytest "$@"
    fi
}

# Function to run linting
run_lint() {
    print_message $YELLOW "Running linting checks..."
    
    print_message $YELLOW "\nRunning Black..."
    black --check .
    
    print_message $YELLOW "\nRunning Flake8..."
    flake8 .
    
    print_message $YELLOW "\nRunning isort..."
    isort --check-only --diff .
}

# Function to fix code style
fix_style() {
    print_message $YELLOW "Fixing code style..."
    
    print_message $YELLOW "\nRunning Black..."
    black .
    
    print_message $YELLOW "\nRunning isort..."
    isort .
}

# Function to run security checks
run_security() {
    print_message $YELLOW "Running security checks..."
    
    print_message $YELLOW "\nRunning Bandit..."
    bandit -r . -x tests/
    
    print_message $YELLOW "\nChecking dependencies for security vulnerabilities..."
    safety check
}

# Function to run type checking
run_types() {
    print_message $YELLOW "Running type checking..."
    mypy .
}

# Function to run all checks
run_all() {
    run_lint
    run_types
    run_security
    run_tests --coverage
}

# Function to watch for changes and run tests
watch_tests() {
    print_message $YELLOW "Watching for changes..."
    
    while true; do
        clear
        run_tests
        
        print_message $YELLOW "\nWatching for changes. Press Ctrl+C to stop."
        inotifywait -q -e modify -r . --exclude '\.git'
    done
}

# Function to show test report
show_report() {
    if [ -f "htmlcov/index.html" ]; then
        python -m http.server --directory htmlcov 8080
    else
        print_message $RED "Coverage report not found. Run tests with coverage first."
        exit 1
    fi
}

# Function to show help message
show_help() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  test [args]        Run tests (pass args to pytest)"
    echo "  coverage           Run tests with coverage report"
    echo "  lint              Run linting checks"
    echo "  fix               Fix code style issues"
    echo "  security          Run security checks"
    echo "  types             Run type checking"
    echo "  all               Run all checks"
    echo "  watch             Watch for changes and run tests"
    echo "  report            Show coverage report in browser"
    echo "  help              Show this help message"
    echo
    echo "Options:"
    echo "  --verbose         Show verbose output"
    echo "  --quiet           Show minimal output"
}

# Check dependencies
check_dependencies

# Parse command line arguments
case "$1" in
    "test")
        shift
        run_tests "$@"
        ;;
    "coverage")
        run_tests --coverage
        ;;
    "lint")
        run_lint
        ;;
    "fix")
        fix_style
        ;;
    "security")
        run_security
        ;;
    "types")
        run_types
        ;;
    "all")
        run_all
        ;;
    "watch")
        watch_tests
        ;;
    "report")
        show_report
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

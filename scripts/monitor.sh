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

# Function to check system health
check_health() {
    print_message $YELLOW "Checking system health..."
    
    # Check MongoDB connection
    print_message $YELLOW "\nChecking MongoDB..."
    if mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        print_message $GREEN "MongoDB: OK"
    else
        print_message $RED "MongoDB: FAILED"
    fi
    
    # Check Redis connection
    print_message $YELLOW "\nChecking Redis..."
    if redis-cli ping &>/dev/null; then
        print_message $GREEN "Redis: OK"
    else
        print_message $RED "Redis: FAILED"
    fi
    
    # Check Celery workers
    print_message $YELLOW "\nChecking Celery workers..."
    if celery -A healmymind inspect ping &>/dev/null; then
        print_message $GREEN "Celery workers: OK"
    else
        print_message $RED "Celery workers: FAILED"
    fi
    
    # Check disk space
    print_message $YELLOW "\nChecking disk space..."
    df -h /
    
    # Check memory usage
    print_message $YELLOW "\nChecking memory usage..."
    free -h
    
    # Check CPU usage
    print_message $YELLOW "\nChecking CPU usage..."
    top -bn1 | head -n 5
}

# Function to monitor logs
monitor_logs() {
    local log_type=${1:-all}
    
    case $log_type in
        "django")
            tail -f logs/django.log
            ;;
        "celery")
            tail -f logs/celery.log
            ;;
        "nginx")
            tail -f logs/nginx-access.log logs/nginx-error.log
            ;;
        "all")
            tail -f logs/*.log
            ;;
        *)
            print_message $RED "Unknown log type: $log_type"
            exit 1
            ;;
    esac
}

# Function to check resource usage
check_resources() {
    print_message $YELLOW "Checking resource usage..."
    
    # Check process memory usage
    print_message $YELLOW "\nProcess Memory Usage:"
    ps aux | head -1
    ps aux | grep -E 'python|celery|gunicorn' | grep -v grep
    
    # Check open files
    print_message $YELLOW "\nOpen Files:"
    lsof -i | grep -E 'python|celery|gunicorn'
    
    # Check network connections
    print_message $YELLOW "\nNetwork Connections:"
    netstat -tuln | grep -E '8000|6379|27017'
}

# Function to monitor performance
monitor_performance() {
    print_message $YELLOW "Monitoring performance..."
    
    # Install required tools if not present
    if ! command -v systat &> /dev/null; then
        print_message $YELLOW "Installing sysstat..."
        sudo apt-get update && sudo apt-get install -y sysstat
    fi
    
    # Monitor CPU, memory, and I/O
    sar 1 10
}

# Function to check security
check_security() {
    print_message $YELLOW "Checking security..."
    
    # Check SSL certificates
    print_message $YELLOW "\nChecking SSL certificates..."
    if [ -f "/etc/letsencrypt/live/api.healmymindai.com/fullchain.pem" ]; then
        openssl x509 -in /etc/letsencrypt/live/api.healmymindai.com/fullchain.pem -text -noout | grep "Not After"
    else
        print_message $RED "SSL certificate not found"
    fi
    
    # Check file permissions
    print_message $YELLOW "\nChecking file permissions..."
    find . -type f -name "*.py" -not -path "./venv/*" -exec ls -l {} \;
    
    # Check open ports
    print_message $YELLOW "\nChecking open ports..."
    netstat -tuln
}

# Function to cleanup old files
cleanup() {
    print_message $YELLOW "Cleaning up old files..."
    
    # Clean up old logs
    find logs -name "*.log.*" -mtime +30 -delete
    
    # Clean up old backups
    find backups -mtime +30 -delete
    
    # Clean up Python cache
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -name "*.pyc" -delete
    
    # Clean up temporary files
    find . -type f -name "*.tmp" -delete
    find . -type f -name "*.bak" -delete
    
    print_message $GREEN "Cleanup completed"
}

# Function to rotate logs
rotate_logs() {
    print_message $YELLOW "Rotating logs..."
    
    # Create backup of current logs
    local timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p logs/archive
    
    for log in logs/*.log; do
        if [ -f "$log" ]; then
            mv "$log" "logs/archive/$(basename "$log").$timestamp"
            touch "$log"
        fi
    done
    
    # Compress old logs
    find logs/archive -type f -mtime +7 -exec gzip {} \;
    
    print_message $GREEN "Log rotation completed"
}

# Function to generate status report
generate_report() {
    local report_file="monitoring_report_$(date +%Y%m%d_%H%M%S).txt"
    
    print_message $YELLOW "Generating status report..."
    
    {
        echo "=== healmymind Status Report ==="
        echo "Generated at: $(date)"
        echo
        
        echo "=== System Status ==="
        df -h /
        echo
        free -h
        echo
        
        echo "=== Service Status ==="
        systemctl status mongodb || true
        echo
        systemctl status redis || true
        echo
        systemctl status nginx || true
        echo
        
        echo "=== Application Logs Summary ==="
        tail -n 50 logs/django.log
        echo
        
        echo "=== Error Logs Summary ==="
        grep -i error logs/*.log | tail -n 50
        echo
        
        echo "=== Security Checks ==="
        netstat -tuln
        echo
        
    } > "reports/$report_file"
    
    print_message $GREEN "Report generated: reports/$report_file"
}

# Function to show help message
show_help() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  health            Check system health"
    echo "  logs [type]       Monitor logs (django|celery|nginx|all)"
    echo "  resources         Check resource usage"
    echo "  performance       Monitor system performance"
    echo "  security         Check security settings"
    echo "  cleanup          Clean up old files"
    echo "  rotate           Rotate log files"
    echo "  report           Generate status report"
    echo "  help             Show this help message"
}

# Create necessary directories
mkdir -p logs reports

# Parse command line arguments
case "$1" in
    "health")
        check_health
        ;;
    "logs")
        monitor_logs "$2"
        ;;
    "resources")
        check_resources
        ;;
    "performance")
        monitor_performance
        ;;
    "security")
        check_security
        ;;
    "cleanup")
        cleanup
        ;;
    "rotate")
        rotate_logs
        ;;
    "report")
        generate_report
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

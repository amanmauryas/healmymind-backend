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

# Function to check if MongoDB is running
check_mongodb() {
    if ! mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        print_message $RED "MongoDB is not running. Please start MongoDB and try again."
        exit 1
    fi
}

# Function to create database backup
backup() {
    print_message $YELLOW "Creating database backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    if mongodump --uri "$MONGODB_URI" --out "$backup_dir"; then
        print_message $GREEN "Backup created successfully at $backup_dir"
    else
        print_message $RED "Backup failed"
        exit 1
    fi
}

# Function to restore database from backup
restore() {
    if [ -z "$1" ]; then
        print_message $RED "Please specify backup directory"
        exit 1
    fi
    
    if [ ! -d "$1" ]; then
        print_message $RED "Backup directory not found: $1"
        exit 1
    }
    
    print_message $YELLOW "Restoring database from backup..."
    
    if mongorestore --uri "$MONGODB_URI" "$1"; then
        print_message $GREEN "Database restored successfully"
    else
        print_message $RED "Database restore failed"
        exit 1
    fi
}

# Function to run migrations
migrate() {
    print_message $YELLOW "Running database migrations..."
    
    # Run migrations for each app
    apps=("users" "tests" "blog" "chat")
    
    for app in "${apps[@]}"; do
        print_message $YELLOW "Running migrations for $app..."
        python manage.py makemigrations $app
        python manage.py migrate $app
    done
    
    # Run any remaining migrations
    python manage.py migrate
    
    print_message $GREEN "Migrations completed successfully"
}

# Function to seed database with initial data
seed() {
    print_message $YELLOW "Seeding database with initial data..."
    
    # Load fixtures for each app
    fixtures=(
        "users/fixtures/initial_users.json"
        "tests/fixtures/initial_tests.json"
        "blog/fixtures/initial_posts.json"
        "chat/fixtures/initial_resources.json"
    )
    
    for fixture in "${fixtures[@]}"; do
        if [ -f "$fixture" ]; then
            print_message $YELLOW "Loading fixture: $fixture"
            python manage.py loaddata $fixture
        fi
    done
    
    print_message $GREEN "Database seeded successfully"
}

# Function to reset database
reset() {
    print_message $YELLOW "Warning: This will delete all data in the database."
    read -p "Are you sure you want to continue? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message $YELLOW "Creating backup before reset..."
        backup
        
        print_message $YELLOW "Dropping database..."
        mongosh "$MONGODB_URI" --eval "db.dropDatabase()"
        
        print_message $YELLOW "Running migrations..."
        migrate
        
        print_message $YELLOW "Seeding database..."
        seed
        
        print_message $GREEN "Database reset completed successfully"
    else
        print_message $YELLOW "Database reset cancelled"
    fi
}

# Function to check database status
status() {
    print_message $YELLOW "Checking database status..."
    
    # Check MongoDB connection
    if mongosh "$MONGODB_URI" --eval "db.adminCommand('ping')" &>/dev/null; then
        print_message $GREEN "MongoDB connection: OK"
    else
        print_message $RED "MongoDB connection: FAILED"
    fi
    
    # Check collections
    collections=$(mongosh "$MONGODB_URI" --quiet --eval "db.getCollectionNames()")
    print_message $YELLOW "Collections:"
    echo "$collections"
    
    # Check database size
    dbstats=$(mongosh "$MONGODB_URI" --quiet --eval "db.stats()")
    print_message $YELLOW "Database stats:"
    echo "$dbstats"
}

# Function to show help message
show_help() {
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  backup              Create database backup"
    echo "  restore [dir]       Restore database from backup"
    echo "  migrate             Run database migrations"
    echo "  seed               Seed database with initial data"
    echo "  reset              Reset database (with backup)"
    echo "  status             Show database status"
    echo "  help               Show this help message"
}

# Check if MongoDB is running
check_mongodb

# Parse command line arguments
case "$1" in
    "backup")
        backup
        ;;
    "restore")
        restore "$2"
        ;;
    "migrate")
        migrate
        ;;
    "seed")
        seed
        ;;
    "reset")
        reset
        ;;
    "status")
        status
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

#!/usr/bin/env python
"""
Script to manage database migrations and schema changes.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

import django
from django.core.management import call_command
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from termcolor import colored

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')
django.setup()


def print_status(message: str, status: str = 'info') -> None:
    """Print colored status messages."""
    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan'
    }
    print(colored(message, colors.get(status, 'white')))


def check_pending_migrations() -> List[str]:
    """Check for any pending migrations."""
    loader = MigrationLoader(connection)
    graph = loader.graph
    pending_migrations = []

    for app_name, migrations in loader.disk_migrations.items():
        for migration_name, _ in migrations.items():
            if (app_name, migration_name) not in loader.applied_migrations:
                pending_migrations.append(f"{app_name}.{migration_name}")

    return pending_migrations


def create_migrations() -> None:
    """Create new migrations for all apps."""
    try:
        print_status("\nChecking for model changes...", 'info')
        call_command('makemigrations')
        print_status("✓ Migrations created successfully", 'success')
    except Exception as e:
        print_status(f"✗ Error creating migrations: {e}", 'error')
        sys.exit(1)


def apply_migrations(app_label: Optional[str] = None) -> None:
    """Apply pending migrations."""
    try:
        print_status("\nApplying migrations...", 'info')
        if app_label:
            call_command('migrate', app_label)
        else:
            call_command('migrate')
        print_status("✓ Migrations applied successfully", 'success')
    except Exception as e:
        print_status(f"✗ Error applying migrations: {e}", 'error')
        sys.exit(1)


def show_migration_status() -> None:
    """Show the status of all migrations."""
    try:
        print_status("\nMigration status:", 'info')
        call_command('showmigrations')
    except Exception as e:
        print_status(f"✗ Error showing migration status: {e}", 'error')
        sys.exit(1)


def check_conflicts() -> None:
    """Check for migration conflicts."""
    try:
        loader = MigrationLoader(connection, ignore_no_migrations=True)
        conflicts = loader.detect_conflicts()

        if conflicts:
            print_status("\nMigration conflicts detected:", 'error')
            for app, names in conflicts.items():
                print_status(f"  {app}: {', '.join(names)}", 'error')
            sys.exit(1)
        else:
            print_status("\n✓ No migration conflicts detected", 'success')
    except Exception as e:
        print_status(f"✗ Error checking conflicts: {e}", 'error')
        sys.exit(1)


def backup_database() -> None:
    """Create a database backup before migrations."""
    try:
        print_status("\nCreating database backup...", 'info')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        backup_file = backup_dir / f'backup_{timestamp}.json'

        call_command('dumpdata', output=str(backup_file))
        print_status(f"✓ Backup created: {backup_file}", 'success')
    except Exception as e:
        print_status(f"✗ Error creating backup: {e}", 'error')
        sys.exit(1)


def verify_schema() -> None:
    """Verify database schema integrity."""
    try:
        print_status("\nVerifying database schema...", 'info')
        call_command('validate_templates')
        call_command('check')
        print_status("✓ Schema verification passed", 'success')
    except Exception as e:
        print_status(f"✗ Schema verification failed: {e}", 'error')
        sys.exit(1)


def main() -> None:
    """Main function to handle migrations."""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description='Database migration management script')
    parser.add_argument('--create', action='store_true', help='Create new migrations')
    parser.add_argument('--apply', action='store_true', help='Apply pending migrations')
    parser.add_argument('--app', help='Specify app label for migrations')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    parser.add_argument('--check', action='store_true', help='Check for conflicts')
    parser.add_argument('--backup', action='store_true', help='Create database backup')
    parser.add_argument('--verify', action='store_true', help='Verify schema integrity')
    parser.add_argument('--all', action='store_true', help='Run all migration tasks')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Check for pending migrations
    pending = check_pending_migrations()
    if pending:
        print_status("\nPending migrations:", 'warning')
        for migration in pending:
            print_status(f"  {migration}", 'warning')
    else:
        print_status("\n✓ No pending migrations", 'success')

    # Execute requested operations
    if args.backup or args.all:
        backup_database()

    if args.check or args.all:
        check_conflicts()

    if args.create or args.all:
        create_migrations()

    if args.verify or args.all:
        verify_schema()

    if args.apply or args.all:
        apply_migrations(args.app)

    if args.status or args.all:
        show_migration_status()


if __name__ == '__main__':
    main()

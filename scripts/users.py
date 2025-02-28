#!/usr/bin/env python
"""
Script to manage users and permissions.
"""
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from termcolor import colored

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')
django.setup()

User = get_user_model()


def print_status(message: str, status: str = 'info') -> None:
    """Print colored status messages."""
    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan'
    }
    print(colored(message, colors.get(status, 'white')))


def create_user(email: str, password: str, is_staff: bool = False, is_superuser: bool = False) -> None:
    """Create a new user."""
    try:
        print_status(f"\nCreating user: {email}", 'info')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        print_status("✓ User created successfully", 'success')
        return user
    
    except Exception as e:
        print_status(f"✗ Error creating user: {e}", 'error')
        return None


def list_users(inactive: bool = False) -> None:
    """List all users."""
    print_status("\nListing users:", 'info')
    
    users = User.objects.all()
    if not inactive:
        users = users.filter(is_active=True)
    
    print("\nEmail                  Staff  Super  Active  Last Login")
    print("-" * 60)
    
    for user in users:
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
        print(f"{user.email:<20}  {user.is_staff!s:<6}  {user.is_superuser!s:<6}  "
              f"{user.is_active!s:<7}  {last_login}")


def create_group(name: str, permissions: List[str]) -> None:
    """Create a new group with permissions."""
    try:
        print_status(f"\nCreating group: {name}", 'info')
        
        group, created = Group.objects.get_or_create(name=name)
        
        # Add permissions
        for perm_name in permissions:
            try:
                app_label, codename = perm_name.split('.')
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                group.permissions.add(perm)
            except Exception as e:
                print_status(f"! Error adding permission {perm_name}: {e}", 'warning')
        
        print_status("✓ Group created successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error creating group: {e}", 'error')


def list_groups() -> None:
    """List all groups and their permissions."""
    print_status("\nListing groups:", 'info')
    
    for group in Group.objects.all():
        print(f"\n{group.name}")
        print("-" * len(group.name))
        
        for perm in group.permissions.all():
            print(f"- {perm.content_type.app_label}.{perm.codename}")


def assign_user_to_group(email: str, group_name: str) -> None:
    """Assign a user to a group."""
    try:
        print_status(f"\nAssigning user {email} to group {group_name}", 'info')
        
        user = User.objects.get(email=email)
        group = Group.objects.get(name=group_name)
        
        user.groups.add(group)
        print_status("✓ User assigned to group successfully", 'success')
    
    except User.DoesNotExist:
        print_status(f"✗ User not found: {email}", 'error')
    except Group.DoesNotExist:
        print_status(f"✗ Group not found: {group_name}", 'error')
    except Exception as e:
        print_status(f"✗ Error assigning user to group: {e}", 'error')


def list_permissions() -> None:
    """List all available permissions."""
    print_status("\nListing available permissions:", 'info')
    
    for perm in Permission.objects.all().order_by('content_type__app_label'):
        print(f"{perm.content_type.app_label}.{perm.codename}: {perm.name}")


def audit_user_access(email: Optional[str] = None) -> None:
    """Audit user permissions and access."""
    print_status("\nAuditing user access:", 'info')
    
    users = User.objects.all()
    if email:
        users = users.filter(email=email)
    
    for user in users:
        print(f"\nUser: {user.email}")
        print("-" * (len(user.email) + 6))
        
        print("\nGroups:")
        for group in user.groups.all():
            print(f"- {group.name}")
        
        print("\nPermissions:")
        for perm in user.get_all_permissions():
            print(f"- {perm}")


def import_users(file_path: str) -> None:
    """Import users from CSV file."""
    try:
        print_status(f"\nImporting users from {file_path}", 'info')
        
        with open(file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    user = create_user(
                        email=row['email'],
                        password=row['password'],
                        is_staff=row.get('is_staff', '').lower() == 'true',
                        is_superuser=row.get('is_superuser', '').lower() == 'true'
                    )
                    
                    if user and 'groups' in row:
                        for group_name in row['groups'].split(','):
                            if group_name.strip():
                                assign_user_to_group(user.email, group_name.strip())
                
                except Exception as e:
                    print_status(f"! Error importing user {row.get('email')}: {e}", 'warning')
        
        print_status("✓ Users imported successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error importing users: {e}", 'error')


def export_users(file_path: str) -> None:
    """Export users to CSV file."""
    try:
        print_status(f"\nExporting users to {file_path}", 'info')
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'is_staff', 'is_superuser', 'is_active', 'groups'])
            
            for user in User.objects.all():
                writer.writerow([
                    user.email,
                    user.is_staff,
                    user.is_superuser,
                    user.is_active,
                    ','.join(g.name for g in user.groups.all())
                ])
        
        print_status("✓ Users exported successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error exporting users: {e}", 'error')


def cleanup_inactive_users(days: int = 90) -> None:
    """Clean up inactive users."""
    try:
        print_status(f"\nCleaning up users inactive for {days} days...", 'info')
        
        cutoff_date = datetime.now() - timedelta(days=days)
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        count = inactive_users.count()
        if count > 0:
            inactive_users.update(is_active=False)
            print_status(f"✓ Deactivated {count} inactive users", 'success')
        else:
            print_status("No inactive users found", 'info')
    
    except Exception as e:
        print_status(f"✗ Error cleaning up users: {e}", 'error')


def main() -> None:
    """Main function to manage users."""
    import argparse

    parser = argparse.ArgumentParser(description='User management script')
    parser.add_argument('--create', nargs=2, metavar=('EMAIL', 'PASSWORD'), help='Create new user')
    parser.add_argument('--staff', action='store_true', help='Create as staff user')
    parser.add_argument('--superuser', action='store_true', help='Create as superuser')
    parser.add_argument('--list-users', action='store_true', help='List all users')
    parser.add_argument('--inactive', action='store_true', help='Include inactive users')
    parser.add_argument('--create-group', nargs='+', metavar=('NAME', 'PERMS'), help='Create group')
    parser.add_argument('--list-groups', action='store_true', help='List all groups')
    parser.add_argument('--assign', nargs=2, metavar=('EMAIL', 'GROUP'), help='Assign user to group')
    parser.add_argument('--permissions', action='store_true', help='List all permissions')
    parser.add_argument('--audit', help='Audit user access')
    parser.add_argument('--import', metavar='FILE', help='Import users from CSV')
    parser.add_argument('--export', metavar='FILE', help='Export users to CSV')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Clean up inactive users')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.create:
        create_user(args.create[0], args.create[1], args.staff, args.superuser)

    if args.list_users:
        list_users(args.inactive)

    if args.create_group:
        create_group(args.create_group[0], args.create_group[1:])

    if args.list_groups:
        list_groups()

    if args.assign:
        assign_user_to_group(args.assign[0], args.assign[1])

    if args.permissions:
        list_permissions()

    if args.audit:
        audit_user_access(args.audit)

    if getattr(args, 'import'):
        import_users(getattr(args, 'import'))

    if args.export:
        export_users(args.export)

    if args.cleanup:
        cleanup_inactive_users(args.cleanup)


if __name__ == '__main__':
    main()

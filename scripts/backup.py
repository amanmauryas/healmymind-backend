#!/usr/bin/env python
"""
Script to handle database backups and restores.
"""
import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import django
from django.conf import settings
from django.core import serializers
from django.core.management import call_command
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


def create_backup_dir() -> Path:
    """Create backup directory if it doesn't exist."""
    backup_dir = BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def backup_database(backup_dir: Path) -> Path:
    """Create database backup."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'db_backup_{timestamp}.json'
    
    try:
        print_status("\nBacking up database...", 'info')
        
        # Get all models
        from django.apps import apps
        all_models = []
        for app_config in apps.get_app_configs():
            all_models.extend(app_config.get_models())
        
        # Create backup
        with open(backup_file, 'w') as f:
            # Serialize each model's data
            for model in all_models:
                data = serializers.serialize('json', model.objects.all())
                json.dump(json.loads(data), f, indent=2)
                f.write('\n')
        
        print_status(f"✓ Database backup created: {backup_file}", 'success')
        return backup_file
    
    except Exception as e:
        print_status(f"✗ Error backing up database: {e}", 'error')
        sys.exit(1)


def backup_media(backup_dir: Path) -> Optional[Path]:
    """Create media files backup."""
    if not settings.MEDIA_ROOT or not Path(settings.MEDIA_ROOT).exists():
        print_status("! No media files to backup", 'warning')
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'media_backup_{timestamp}.tar.gz'
    
    try:
        print_status("\nBacking up media files...", 'info')
        
        with tarfile.open(backup_file, 'w:gz') as tar:
            tar.add(settings.MEDIA_ROOT, arcname='media')
        
        print_status(f"✓ Media backup created: {backup_file}", 'success')
        return backup_file
    
    except Exception as e:
        print_status(f"✗ Error backing up media files: {e}", 'error')
        sys.exit(1)


def create_full_backup() -> None:
    """Create full backup including database and media files."""
    backup_dir = create_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    full_backup_dir = backup_dir / f'full_backup_{timestamp}'
    full_backup_dir.mkdir(exist_ok=True)
    
    try:
        # Backup database
        db_backup = backup_database(full_backup_dir)
        
        # Backup media files
        media_backup = backup_media(full_backup_dir)
        
        # Create metadata file
        metadata = {
            'timestamp': timestamp,
            'django_version': django.get_version(),
            'database': str(db_backup),
            'media': str(media_backup) if media_backup else None
        }
        
        with open(full_backup_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create archive
        archive_name = f'full_backup_{timestamp}.tar.gz'
        with tarfile.open(backup_dir / archive_name, 'w:gz') as tar:
            tar.add(full_backup_dir, arcname=f'full_backup_{timestamp}')
        
        # Clean up temporary directory
        shutil.rmtree(full_backup_dir)
        
        print_status(f"\n✓ Full backup created: {backup_dir / archive_name}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error creating full backup: {e}", 'error')
        sys.exit(1)


def restore_database(backup_file: Path) -> None:
    """Restore database from backup."""
    try:
        print_status("\nRestoring database...", 'info')
        
        # Clear existing data
        call_command('flush', interactive=False)
        
        # Load backup data
        with open(backup_file) as f:
            data = json.load(f)
            for obj in serializers.deserialize('json', json.dumps(data)):
                obj.save()
        
        print_status("✓ Database restored successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error restoring database: {e}", 'error')
        sys.exit(1)


def restore_media(backup_file: Path) -> None:
    """Restore media files from backup."""
    try:
        print_status("\nRestoring media files...", 'info')
        
        # Clear existing media directory
        if Path(settings.MEDIA_ROOT).exists():
            shutil.rmtree(settings.MEDIA_ROOT)
        
        # Extract backup
        with tarfile.open(backup_file, 'r:gz') as tar:
            tar.extractall(Path(settings.MEDIA_ROOT).parent)
        
        print_status("✓ Media files restored successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error restoring media files: {e}", 'error')
        sys.exit(1)


def restore_full_backup(backup_file: Path) -> None:
    """Restore full backup."""
    try:
        print_status("\nRestoring full backup...", 'info')
        
        # Create temporary directory
        temp_dir = BASE_DIR / 'temp_restore'
        temp_dir.mkdir(exist_ok=True)
        
        # Extract archive
        with tarfile.open(backup_file, 'r:gz') as tar:
            tar.extractall(temp_dir)
        
        # Read metadata
        backup_dir = next(temp_dir.iterdir())  # Get the extracted directory
        with open(backup_dir / 'metadata.json') as f:
            metadata = json.load(f)
        
        # Restore database
        db_backup = backup_dir / Path(metadata['database']).name
        restore_database(db_backup)
        
        # Restore media files if they exist
        if metadata['media']:
            media_backup = backup_dir / Path(metadata['media']).name
            restore_media(media_backup)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        print_status("\n✓ Full backup restored successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error restoring full backup: {e}", 'error')
        sys.exit(1)


def list_backups() -> None:
    """List available backups."""
    backup_dir = create_backup_dir()
    
    print_status("\nAvailable backups:", 'info')
    
    # List database backups
    db_backups = list(backup_dir.glob('db_backup_*.json'))
    if db_backups:
        print("\nDatabase backups:")
        for backup in db_backups:
            size = backup.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  {backup.name} ({size:.2f} MB)")
    
    # List media backups
    media_backups = list(backup_dir.glob('media_backup_*.tar.gz'))
    if media_backups:
        print("\nMedia backups:")
        for backup in media_backups:
            size = backup.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  {backup.name} ({size:.2f} MB)")
    
    # List full backups
    full_backups = list(backup_dir.glob('full_backup_*.tar.gz'))
    if full_backups:
        print("\nFull backups:")
        for backup in full_backups:
            size = backup.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  {backup.name} ({size:.2f} MB)")


def cleanup_old_backups(days: int = 30) -> None:
    """Clean up backups older than specified days."""
    backup_dir = create_backup_dir()
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    try:
        print_status(f"\nCleaning up backups older than {days} days...", 'info')
        
        for backup in backup_dir.glob('*_backup_*'):
            if backup.stat().st_mtime < cutoff:
                backup.unlink()
                print(f"Deleted: {backup.name}")
        
        print_status("✓ Cleanup completed", 'success')
    
    except Exception as e:
        print_status(f"✗ Error cleaning up backups: {e}", 'error')
        sys.exit(1)


def main() -> None:
    """Main function to handle backup operations."""
    import argparse

    parser = argparse.ArgumentParser(description='Backup management script')
    parser.add_argument('--create', choices=['db', 'media', 'full'], help='Create backup')
    parser.add_argument('--restore', help='Restore from backup file')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Clean up old backups')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.create:
        if args.create == 'db':
            backup_database(create_backup_dir())
        elif args.create == 'media':
            backup_media(create_backup_dir())
        else:
            create_full_backup()

    if args.restore:
        restore_path = Path(args.restore)
        if not restore_path.exists():
            print_status(f"✗ Backup file not found: {restore_path}", 'error')
            sys.exit(1)
        
        if restore_path.suffix == '.json':
            restore_database(restore_path)
        elif restore_path.name.startswith('media_backup_'):
            restore_media(restore_path)
        elif restore_path.name.startswith('full_backup_'):
            restore_full_backup(restore_path)
        else:
            print_status("✗ Invalid backup file", 'error')
            sys.exit(1)

    if args.list:
        list_backups()

    if args.cleanup:
        cleanup_old_backups(args.cleanup)


if __name__ == '__main__':
    main()

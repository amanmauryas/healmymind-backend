#!/usr/bin/env python
"""
Script to manage logs and error tracking.
"""
import gzip
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import django
from django.conf import settings
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


def setup_logging() -> None:
    """Set up logging configuration."""
    try:
        print_status("\nSetting up logging configuration...", 'info')
        
        logs_dir = BASE_DIR / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname} {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': logs_dir / 'app.log',
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 5,
                    'formatter': 'verbose',
                },
                'error_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': logs_dir / 'error.log',
                    'maxBytes': 1024 * 1024 * 5,  # 5 MB
                    'backupCount': 5,
                    'formatter': 'verbose',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['file'],
                    'level': 'INFO',
                    'propagate': True,
                },
                'healmymind': {
                    'handlers': ['file', 'error_file'],
                    'level': 'INFO',
                    'propagate': True,
                },
            },
        })
        
        print_status("✓ Logging configuration set up successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error setting up logging: {e}", 'error')
        sys.exit(1)


def rotate_logs() -> None:
    """Rotate log files."""
    try:
        print_status("\nRotating log files...", 'info')
        
        logs_dir = BASE_DIR / 'logs'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for log_file in logs_dir.glob('*.log'):
            if log_file.stat().st_size > 0:
                # Create archive directory
                archive_dir = logs_dir / 'archive'
                archive_dir.mkdir(exist_ok=True)
                
                # Compress and move log file
                archive_path = archive_dir / f'{log_file.stem}_{timestamp}.log.gz'
                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Clear original log file
                log_file.write_text('')
        
        print_status("✓ Log files rotated successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error rotating logs: {e}", 'error')
        sys.exit(1)


def analyze_errors(days: int = 7) -> None:
    """Analyze error logs for patterns."""
    print_status(f"\nAnalyzing error logs for the past {days} days...", 'info')
    
    logs_dir = BASE_DIR / 'logs'
    error_log = logs_dir / 'error.log'
    
    if not error_log.exists():
        print_status("No error log file found", 'warning')
        return
    
    # Parse error logs
    errors: Dict[str, List[Dict]] = {}
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with open(error_log) as f:
        for line in f:
            try:
                # Parse log entry
                match = re.match(r'ERROR (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+)', line)
                if match:
                    timestamp_str, module = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    
                    if timestamp >= cutoff_date:
                        error_type = line.split()[3] if len(line.split()) > 3 else 'Unknown'
                        if error_type not in errors:
                            errors[error_type] = []
                        errors[error_type].append({
                            'timestamp': timestamp_str,
                            'module': module,
                            'message': line.strip()
                        })
            except Exception:
                continue
    
    # Print analysis
    if errors:
        print("\nError Summary:")
        for error_type, instances in sorted(errors.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{error_type}: {len(instances)} occurrences")
            print("Most recent occurrence:")
            print(instances[-1]['message'])
    else:
        print_status("No errors found in the specified time period", 'success')


def export_logs(output_file: str) -> None:
    """Export logs to JSON format."""
    try:
        print_status("\nExporting logs...", 'info')
        
        logs_dir = BASE_DIR / 'logs'
        logs_data = {}
        
        for log_file in logs_dir.glob('*.log'):
            logs_data[log_file.stem] = []
            with open(log_file) as f:
                for line in f:
                    logs_data[log_file.stem].append(line.strip())
        
        # Export to JSON
        with open(output_file, 'w') as f:
            json.dump(logs_data, f, indent=2)
        
        print_status(f"✓ Logs exported to {output_file}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error exporting logs: {e}", 'error')
        sys.exit(1)


def cleanup_old_logs(days: int = 30) -> None:
    """Clean up old log archives."""
    try:
        print_status(f"\nCleaning up logs older than {days} days...", 'info')
        
        logs_dir = BASE_DIR / 'logs'
        archive_dir = logs_dir / 'archive'
        
        if not archive_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for log_file in archive_dir.glob('*.log.gz'):
            try:
                # Extract date from filename
                date_str = re.search(r'_(\d{8})_', log_file.name).group(1)
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            except Exception:
                continue
        
        print_status(f"✓ Deleted {deleted_count} old log files", 'success')
    
    except Exception as e:
        print_status(f"✗ Error cleaning up logs: {e}", 'error')
        sys.exit(1)


def monitor_log_size() -> None:
    """Monitor log file sizes."""
    print_status("\nMonitoring log file sizes...", 'info')
    
    logs_dir = BASE_DIR / 'logs'
    total_size = 0
    
    print("\nCurrent log files:")
    for log_file in logs_dir.glob('*.log'):
        size = log_file.stat().st_size
        total_size += size
        print(f"{log_file.name}: {size / 1024 / 1024:.2f} MB")
    
    print(f"\nTotal size: {total_size / 1024 / 1024:.2f} MB")
    
    if total_size > 100 * 1024 * 1024:  # 100 MB
        print_status("! Log files are getting large, consider rotation", 'warning')


def tail_logs(lines: int = 50, follow: bool = False) -> None:
    """Display recent log entries."""
    print_status(f"\nShowing last {lines} log lines:", 'info')
    
    logs_dir = BASE_DIR / 'logs'
    app_log = logs_dir / 'app.log'
    
    if not app_log.exists():
        print_status("No log file found", 'error')
        return
    
    try:
        if follow:
            # Follow log file in real-time
            import time
            with open(app_log) as f:
                # Go to end of file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(line.strip())
                    else:
                        time.sleep(0.1)
        else:
            # Show last n lines
            with open(app_log) as f:
                for line in list(f)[-lines:]:
                    print(line.strip())
    
    except KeyboardInterrupt:
        print("\nStopped following logs")
    except Exception as e:
        print_status(f"✗ Error reading logs: {e}", 'error')


def main() -> None:
    """Main function to manage logs."""
    import argparse

    parser = argparse.ArgumentParser(description='Log management script')
    parser.add_argument('--setup', action='store_true', help='Set up logging configuration')
    parser.add_argument('--rotate', action='store_true', help='Rotate log files')
    parser.add_argument('--analyze', type=int, metavar='DAYS', help='Analyze errors for past N days')
    parser.add_argument('--export', help='Export logs to JSON file')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Clean up logs older than N days')
    parser.add_argument('--monitor', action='store_true', help='Monitor log sizes')
    parser.add_argument('--tail', type=int, metavar='LINES', help='Show recent log entries')
    parser.add_argument('--follow', action='store_true', help='Follow log output in real-time')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.setup:
        setup_logging()

    if args.rotate:
        rotate_logs()

    if args.analyze:
        analyze_errors(args.analyze)

    if args.export:
        export_logs(args.export)

    if args.cleanup:
        cleanup_old_logs(args.cleanup)

    if args.monitor:
        monitor_log_size()

    if args.tail:
        tail_logs(args.tail, args.follow)


if __name__ == '__main__':
    main()

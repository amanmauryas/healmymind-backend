#!/usr/bin/env python
"""
Script to manage static files and assets.
"""
import hashlib
import os
import shutil
import subprocess
import sys
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


def collect_static() -> None:
    """Collect static files."""
    try:
        print_status("\nCollecting static files...", 'info')
        
        # Clear existing static files
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            shutil.rmtree(static_root)
        
        # Collect static files
        call_command('collectstatic', interactive=False, verbosity=0)
        
        print_status("✓ Static files collected successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error collecting static files: {e}", 'error')
        sys.exit(1)


def compress_assets() -> None:
    """Compress static assets."""
    try:
        print_status("\nCompressing static assets...", 'info')
        
        static_root = Path(settings.STATIC_ROOT)
        
        # Compress JavaScript files
        for js_file in static_root.rglob('*.js'):
            if not js_file.name.endswith('.min.js'):
                print(f"Compressing {js_file.relative_to(static_root)}...")
                subprocess.run(['terser', str(js_file), '-o', str(js_file)], check=True)
        
        # Compress CSS files
        for css_file in static_root.rglob('*.css'):
            if not css_file.name.endswith('.min.css'):
                print(f"Compressing {css_file.relative_to(static_root)}...")
                subprocess.run(['cleancss', '-o', str(css_file), str(css_file)], check=True)
        
        print_status("✓ Assets compressed successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error compressing assets: {e}", 'error')
        sys.exit(1)


def optimize_images() -> None:
    """Optimize image files."""
    try:
        print_status("\nOptimizing images...", 'info')
        
        static_root = Path(settings.STATIC_ROOT)
        
        # Optimize PNG files
        for png_file in static_root.rglob('*.png'):
            print(f"Optimizing {png_file.relative_to(static_root)}...")
            subprocess.run(['optipng', '-quiet', str(png_file)], check=True)
        
        # Optimize JPEG files
        for jpg_file in static_root.rglob('*.{jpg,jpeg}'):
            print(f"Optimizing {jpg_file.relative_to(static_root)}...")
            subprocess.run(['jpegoptim', '--strip-all', str(jpg_file)], check=True)
        
        print_status("✓ Images optimized successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error optimizing images: {e}", 'error')
        sys.exit(1)


def generate_hashes() -> Dict[str, str]:
    """Generate file hashes for cache busting."""
    try:
        print_status("\nGenerating file hashes...", 'info')
        
        static_root = Path(settings.STATIC_ROOT)
        hashes = {}
        
        for file_path in static_root.rglob('*.*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(static_root)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                hashes[str(relative_path)] = file_hash
        
        # Save hashes to JSON file
        import json
        with open(static_root / 'hashes.json', 'w') as f:
            json.dump(hashes, f, indent=2)
        
        print_status("✓ File hashes generated successfully", 'success')
        return hashes
    
    except Exception as e:
        print_status(f"✗ Error generating file hashes: {e}", 'error')
        sys.exit(1)


def check_missing_assets() -> None:
    """Check for missing static files."""
    print_status("\nChecking for missing assets...", 'info')
    
    static_root = Path(settings.STATIC_ROOT)
    missing_files = []
    
    # Check required static files
    required_files = [
        'css/styles.css',
        'js/main.js',
        'img/logo.png',
        'favicon.ico'
    ]
    
    for file_path in required_files:
        if not (static_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_status("! Missing required files:", 'warning')
        for file_path in missing_files:
            print(f"  - {file_path}")
    else:
        print_status("✓ All required files present", 'success')


def analyze_size() -> None:
    """Analyze static file sizes."""
    print_status("\nAnalyzing static file sizes...", 'info')
    
    static_root = Path(settings.STATIC_ROOT)
    size_by_type: Dict[str, int] = {}
    large_files: List[Tuple[Path, int]] = []
    
    for file_path in static_root.rglob('*.*'):
        if file_path.is_file():
            size = file_path.stat().st_size
            ext = file_path.suffix.lower()
            
            # Track size by file type
            size_by_type[ext] = size_by_type.get(ext, 0) + size
            
            # Track large files (>1MB)
            if size > 1024 * 1024:
                large_files.append((file_path, size))
    
    # Print size by type
    print("\nSize by file type:")
    for ext, size in sorted(size_by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"{ext}: {size / 1024 / 1024:.2f} MB")
    
    # Print large files
    if large_files:
        print("\nLarge files (>1MB):")
        for file_path, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            print(f"{file_path.relative_to(static_root)}: {size / 1024 / 1024:.2f} MB")


def create_manifest() -> None:
    """Create a static files manifest."""
    try:
        print_status("\nCreating static files manifest...", 'info')
        
        static_root = Path(settings.STATIC_ROOT)
        manifest = {
            'version': '1.0',
            'timestamp': str(timezone.now()),
            'files': {}
        }
        
        for file_path in static_root.rglob('*.*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(static_root))
                manifest['files'][relative_path] = {
                    'size': file_path.stat().st_size,
                    'hash': hashlib.md5(file_path.read_bytes()).hexdigest()
                }
        
        # Save manifest
        with open(static_root / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print_status("✓ Manifest created successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error creating manifest: {e}", 'error')
        sys.exit(1)


def sync_cdn() -> None:
    """Sync static files with CDN."""
    try:
        print_status("\nSyncing files with CDN...", 'info')
        
        # Example using AWS S3
        if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            subprocess.run([
                'aws', 's3', 'sync',
                str(settings.STATIC_ROOT),
                f's3://{settings.AWS_STORAGE_BUCKET_NAME}/static/',
                '--delete'
            ], check=True)
            print_status("✓ Files synced with CDN successfully", 'success')
        else:
            print_status("! CDN settings not configured", 'warning')
    
    except Exception as e:
        print_status(f"✗ Error syncing with CDN: {e}", 'error')
        sys.exit(1)


def main() -> None:
    """Main function to manage static assets."""
    import argparse
    from django.utils import timezone

    parser = argparse.ArgumentParser(description='Static assets management script')
    parser.add_argument('--collect', action='store_true', help='Collect static files')
    parser.add_argument('--compress', action='store_true', help='Compress assets')
    parser.add_argument('--optimize', action='store_true', help='Optimize images')
    parser.add_argument('--hashes', action='store_true', help='Generate file hashes')
    parser.add_argument('--check', action='store_true', help='Check for missing assets')
    parser.add_argument('--analyze', action='store_true', help='Analyze file sizes')
    parser.add_argument('--manifest', action='store_true', help='Create manifest')
    parser.add_argument('--sync', action='store_true', help='Sync with CDN')
    parser.add_argument('--all', action='store_true', help='Run all tasks')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.collect or args.all:
        collect_static()

    if args.compress or args.all:
        compress_assets()

    if args.optimize or args.all:
        optimize_images()

    if args.hashes or args.all:
        generate_hashes()

    if args.check or args.all:
        check_missing_assets()

    if args.analyze or args.all:
        analyze_size()

    if args.manifest or args.all:
        create_manifest()

    if args.sync or args.all:
        sync_cdn()


if __name__ == '__main__':
    main()

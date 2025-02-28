#!/usr/bin/env python
"""
Script to perform security audits and checks.
"""
import os
import re
import ssl
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import django
import requests
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


def check_dependencies() -> List[Dict[str, str]]:
    """Check dependencies for known vulnerabilities."""
    try:
        import pkg_resources
        from safety.safety import check as safety_check
        from safety.util import read_requirements
        
        print_status("\nChecking dependencies for vulnerabilities...", 'info')
        
        # Get installed packages
        packages = [
            {'name': pkg.key, 'version': pkg.version}
            for pkg in pkg_resources.working_set
        ]
        
        # Check for vulnerabilities
        vulns = safety_check(packages=packages)
        
        if vulns:
            print_status(f"Found {len(vulns)} vulnerabilities:", 'error')
            for vuln in vulns:
                print(f"\nPackage: {vuln.package}")
                print(f"Version: {vuln.version}")
                print(f"CVE: {vuln.cve}")
                print(f"Description: {vuln.description}")
        else:
            print_status("✓ No known vulnerabilities found", 'success')
        
        return vulns
    
    except ImportError:
        print_status("! Safety package not installed. Install with: pip install safety", 'warning')
        return []


def check_ssl_config() -> None:
    """Check SSL/TLS configuration."""
    print_status("\nChecking SSL/TLS configuration...", 'info')
    
    # Check SSL version
    print(f"SSL Version: {ssl.OPENSSL_VERSION}")
    
    # Check SSL settings
    ssl_settings = {
        'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0),
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False),
        'SECURE_HSTS_PRELOAD': getattr(settings, 'SECURE_HSTS_PRELOAD', False),
        'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False)
    }
    
    for setting, value in ssl_settings.items():
        status = 'success' if value else 'warning'
        print_status(f"{setting}: {value}", status)


def check_secret_key() -> None:
    """Check if SECRET_KEY is secure."""
    print_status("\nChecking SECRET_KEY...", 'info')
    
    secret_key = getattr(settings, 'SECRET_KEY', '')
    
    if not secret_key:
        print_status("✗ SECRET_KEY is not set!", 'error')
    elif len(secret_key) < 50:
        print_status("! SECRET_KEY might be too short", 'warning')
    elif secret_key == 'your-secret-key-here':
        print_status("✗ Using default SECRET_KEY!", 'error')
    else:
        print_status("✓ SECRET_KEY appears to be properly configured", 'success')


def scan_for_secrets(path: str = '.') -> List[Tuple[str, str, int]]:
    """Scan files for potential secrets."""
    print_status("\nScanning for potential secrets in code...", 'info')
    
    secrets_found: List[Tuple[str, str, int]] = []
    patterns = {
        'AWS Key': r'AKIA[0-9A-Z]{16}',
        'Private Key': r'-----BEGIN (?:RSA )?PRIVATE KEY-----',
        'API Key': r'api[_-]?key[_-]?(?:[\w\d]{32}|[\w\d]{16})',
        'Password': r'password[_-]?[\w\d]{8,}',
        'Token': r'token[_-]?[\w\d]{32,}',
    }
    
    exclude_dirs = {'.git', 'venv', '__pycache__', 'node_modules'}
    
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.yml', '.yaml', '.env')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath) as f:
                        for i, line in enumerate(f, 1):
                            for pattern_name, pattern in patterns.items():
                                if re.search(pattern, line):
                                    secrets_found.append((filepath, pattern_name, i))
                except Exception:
                    continue
    
    if secrets_found:
        print_status(f"Found {len(secrets_found)} potential secrets:", 'warning')
        for file, pattern, line in secrets_found:
            print(f"{file}:{line} - Potential {pattern}")
    else:
        print_status("✓ No potential secrets found", 'success')
    
    return secrets_found


def check_security_headers() -> None:
    """Check security headers configuration."""
    print_status("\nChecking security headers...", 'info')
    
    required_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': None,
        'Strict-Transport-Security': None,
        'Referrer-Policy': None
    }
    
    middleware = getattr(settings, 'MIDDLEWARE', [])
    security_middleware = 'django.middleware.security.SecurityMiddleware'
    
    if security_middleware not in middleware:
        print_status("✗ SecurityMiddleware not enabled!", 'error')
    
    for header, expected in required_headers.items():
        if expected:
            status = 'success' if getattr(settings, f'SECURE_{header.replace("-", "_")}', None) == expected else 'warning'
            print_status(f"{header}: {expected}", status)
        else:
            if not getattr(settings, f'SECURE_{header.replace("-", "_")}', None):
                print_status(f"! {header} not configured", 'warning')


def check_debug_settings() -> None:
    """Check debug-related settings."""
    print_status("\nChecking debug settings...", 'info')
    
    debug = getattr(settings, 'DEBUG', False)
    status = 'error' if debug else 'success'
    print_status(f"DEBUG: {debug}", status)
    
    if debug:
        print_status("! DEBUG should be False in production", 'warning')
    
    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    if not allowed_hosts or '*' in allowed_hosts:
        print_status("✗ ALLOWED_HOSTS not properly configured", 'error')
    else:
        print_status("✓ ALLOWED_HOSTS properly configured", 'success')


def check_database_security() -> None:
    """Check database security settings."""
    print_status("\nChecking database security...", 'info')
    
    databases = getattr(settings, 'DATABASES', {})
    default_db = databases.get('default', {})
    
    # Check connection security
    if default_db.get('ENGINE') == 'django.db.backends.postgresql':
        if not default_db.get('SSL'):
            print_status("! Database SSL not enabled", 'warning')
    
    # Check connection credentials
    if 'PASSWORD' in default_db:
        password = default_db['PASSWORD']
        if not password or password in ['password', 'admin', '']:
            print_status("✗ Using weak database password", 'error')
    
    # Check connection timeout
    if not default_db.get('CONN_MAX_AGE'):
        print_status("! Database connection timeout not set", 'warning')


def check_file_permissions() -> None:
    """Check file permissions."""
    print_status("\nChecking file permissions...", 'info')
    
    critical_files = [
        '.env',
        'settings.py',
        'local_settings.py'
    ]
    
    for file in critical_files:
        path = BASE_DIR / file
        if path.exists():
            try:
                mode = oct(path.stat().st_mode)[-3:]
                if mode not in ['600', '400']:
                    print_status(f"! {file} has loose permissions: {mode}", 'warning')
            except Exception:
                print_status(f"! Could not check permissions for {file}", 'warning')


def check_cors_settings() -> None:
    """Check CORS settings."""
    print_status("\nChecking CORS settings...", 'info')
    
    cors_origin_allow_all = getattr(settings, 'CORS_ORIGIN_ALLOW_ALL', False)
    if cors_origin_allow_all:
        print_status("✗ CORS_ORIGIN_ALLOW_ALL is True", 'error')
    
    cors_origins = getattr(settings, 'CORS_ORIGIN_WHITELIST', [])
    if not cors_origins:
        print_status("! No CORS origins configured", 'warning')
    else:
        print("Allowed CORS origins:")
        for origin in cors_origins:
            print(f"  - {origin}")


def main() -> None:
    """Main function to run security checks."""
    import argparse

    parser = argparse.ArgumentParser(description='Security audit script')
    parser.add_argument('--dependencies', action='store_true', help='Check dependencies')
    parser.add_argument('--ssl', action='store_true', help='Check SSL configuration')
    parser.add_argument('--secrets', action='store_true', help='Scan for secrets')
    parser.add_argument('--headers', action='store_true', help='Check security headers')
    parser.add_argument('--debug', action='store_true', help='Check debug settings')
    parser.add_argument('--database', action='store_true', help='Check database security')
    parser.add_argument('--permissions', action='store_true', help='Check file permissions')
    parser.add_argument('--cors', action='store_true', help='Check CORS settings')
    parser.add_argument('--all', action='store_true', help='Run all checks')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.dependencies or args.all:
        check_dependencies()

    if args.ssl or args.all:
        check_ssl_config()
        check_secret_key()

    if args.secrets or args.all:
        scan_for_secrets()

    if args.headers or args.all:
        check_security_headers()

    if args.debug or args.all:
        check_debug_settings()

    if args.database or args.all:
        check_database_security()

    if args.permissions or args.all:
        check_file_permissions()

    if args.cors or args.all:
        check_cors_settings()


if __name__ == '__main__':
    main()

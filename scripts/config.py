#!/usr/bin/env python
"""
Script to manage environment variables and configuration.
"""
import json
import os
import re
import secrets
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


def validate_env_file() -> bool:
    """Validate environment file against example."""
    try:
        print_status("\nValidating environment file...", 'info')
        
        env_file = BASE_DIR / '.env'
        example_file = BASE_DIR / '.env.example'
        
        if not example_file.exists():
            print_status("✗ .env.example file not found", 'error')
            return False
        
        if not env_file.exists():
            print_status("✗ .env file not found", 'error')
            return False
        
        # Read both files
        env_vars = set()
        example_vars = set()
        
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    var_name = line.split('=')[0].strip()
                    env_vars.add(var_name)
        
        with open(example_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    var_name = line.split('=')[0].strip()
                    example_vars.add(var_name)
        
        # Check for missing variables
        missing_vars = example_vars - env_vars
        if missing_vars:
            print_status("! Missing environment variables:", 'warning')
            for var in missing_vars:
                print(f"  - {var}")
            return False
        
        # Check for extra variables
        extra_vars = env_vars - example_vars
        if extra_vars:
            print_status("! Extra environment variables:", 'warning')
            for var in extra_vars:
                print(f"  - {var}")
        
        print_status("✓ Environment file validation passed", 'success')
        return True
    
    except Exception as e:
        print_status(f"✗ Error validating environment file: {e}", 'error')
        return False


def generate_secret_key() -> str:
    """Generate a new Django secret key."""
    return secrets.token_urlsafe(50)


def update_env_var(name: str, value: str) -> None:
    """Update or add environment variable."""
    try:
        env_file = BASE_DIR / '.env'
        
        # Read existing content
        if env_file.exists():
            content = env_file.read_text()
            
            # Check if variable exists
            pattern = re.compile(f'^{name}=.*$', re.MULTILINE)
            if pattern.search(content):
                # Update existing variable
                content = pattern.sub(f'{name}={value}', content)
            else:
                # Add new variable
                content += f'\n{name}={value}'
            
            env_file.write_text(content)
        else:
            # Create new file
            env_file.write_text(f'{name}={value}\n')
        
        print_status(f"✓ Updated {name}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error updating environment variable: {e}", 'error')


def encrypt_secrets() -> None:
    """Encrypt sensitive environment variables."""
    try:
        from cryptography.fernet import Fernet
        print_status("\nEncrypting sensitive variables...", 'info')
        
        # Generate key if not exists
        key_file = BASE_DIR / '.env.key'
        if not key_file.exists():
            key = Fernet.generate_key()
            key_file.write_bytes(key)
        else:
            key = key_file.read_bytes()
        
        f = Fernet(key)
        env_file = BASE_DIR / '.env'
        
        if not env_file.exists():
            print_status("✗ .env file not found", 'error')
            return
        
        # Encrypt sensitive variables
        sensitive_vars = {'SECRET_KEY', 'DATABASE_URL', 'AWS_SECRET_KEY'}
        content = env_file.read_text()
        encrypted = []
        
        for line in content.splitlines():
            if line.strip() and not line.startswith('#'):
                name = line.split('=')[0].strip()
                if name in sensitive_vars and not line.endswith('=='):  # Not already encrypted
                    value = line.split('=', 1)[1].strip()
                    encrypted_value = f.encrypt(value.encode()).decode()
                    encrypted.append(f'{name}={encrypted_value}')
                else:
                    encrypted.append(line)
        
        # Save encrypted file
        env_file.write_text('\n'.join(encrypted))
        print_status("✓ Sensitive variables encrypted", 'success')
    
    except ImportError:
        print_status("! cryptography package not installed", 'warning')
    except Exception as e:
        print_status(f"✗ Error encrypting secrets: {e}", 'error')


def decrypt_secrets() -> None:
    """Decrypt sensitive environment variables."""
    try:
        from cryptography.fernet import Fernet
        print_status("\nDecrypting sensitive variables...", 'info')
        
        key_file = BASE_DIR / '.env.key'
        if not key_file.exists():
            print_status("✗ Encryption key not found", 'error')
            return
        
        key = key_file.read_bytes()
        f = Fernet(key)
        env_file = BASE_DIR / '.env'
        
        if not env_file.exists():
            print_status("✗ .env file not found", 'error')
            return
        
        # Decrypt sensitive variables
        content = env_file.read_text()
        decrypted = []
        
        for line in content.splitlines():
            if line.strip() and not line.startswith('#'):
                try:
                    name, value = line.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    if value.endswith('=='):  # Likely encrypted
                        decrypted_value = f.decrypt(value.encode()).decode()
                        decrypted.append(f'{name}={decrypted_value}')
                    else:
                        decrypted.append(line)
                except Exception:
                    decrypted.append(line)
            else:
                decrypted.append(line)
        
        # Save decrypted file
        env_file.write_text('\n'.join(decrypted))
        print_status("✓ Sensitive variables decrypted", 'success')
    
    except ImportError:
        print_status("! cryptography package not installed", 'warning')
    except Exception as e:
        print_status(f"✗ Error decrypting secrets: {e}", 'error')


def check_security() -> None:
    """Check security of configuration."""
    print_status("\nChecking configuration security...", 'info')
    
    issues = []
    
    # Check DEBUG setting
    if settings.DEBUG:
        issues.append("DEBUG is enabled")
    
    # Check SECRET_KEY
    if settings.SECRET_KEY in {'your-secret-key-here', 'changeme', ''}:
        issues.append("Using default SECRET_KEY")
    
    # Check ALLOWED_HOSTS
    if not settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS:
        issues.append("ALLOWED_HOSTS not properly configured")
    
    # Check database configuration
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        issues.append("Using SQLite database in production")
    
    # Check security middleware
    security_middleware = 'django.middleware.security.SecurityMiddleware'
    if security_middleware not in settings.MIDDLEWARE:
        issues.append("SecurityMiddleware not enabled")
    
    if issues:
        print_status("! Security issues found:", 'warning')
        for issue in issues:
            print(f"  - {issue}")
    else:
        print_status("✓ No security issues found", 'success')


def export_config() -> None:
    """Export configuration to JSON format."""
    try:
        print_status("\nExporting configuration...", 'info')
        
        config = {
            'DEBUG': settings.DEBUG,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'DATABASES': {
                name: {k: v for k, v in conf.items() if k != 'PASSWORD'}
                for name, conf in settings.DATABASES.items()
            },
            'INSTALLED_APPS': settings.INSTALLED_APPS,
            'MIDDLEWARE': settings.MIDDLEWARE,
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        
        output_file = BASE_DIR / 'config.json'
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_status(f"✓ Configuration exported to {output_file}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error exporting configuration: {e}", 'error')


def main() -> None:
    """Main function to manage configuration."""
    import argparse

    parser = argparse.ArgumentParser(description='Configuration management script')
    parser.add_argument('--validate', action='store_true', help='Validate environment file')
    parser.add_argument('--generate-key', action='store_true', help='Generate new secret key')
    parser.add_argument('--set', nargs=2, metavar=('NAME', 'VALUE'), help='Set environment variable')
    parser.add_argument('--encrypt', action='store_true', help='Encrypt sensitive variables')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt sensitive variables')
    parser.add_argument('--check', action='store_true', help='Check configuration security')
    parser.add_argument('--export', action='store_true', help='Export configuration to JSON')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.validate:
        validate_env_file()

    if args.generate_key:
        key = generate_secret_key()
        print(f"Generated secret key: {key}")

    if args.set:
        update_env_var(args.set[0], args.set[1])

    if args.encrypt:
        encrypt_secrets()

    if args.decrypt:
        decrypt_secrets()

    if args.check:
        check_security()

    if args.export:
        export_config()


if __name__ == '__main__':
    main()

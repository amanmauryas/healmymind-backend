#!/usr/bin/env python
"""
Script to manage email templates and notifications.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import django
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.core.management import call_command
from django.template import Context, Template
from django.template.loader import render_to_string
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


def create_template(name: str, subject: str, html_content: str, text_content: str) -> None:
    """Create or update an email template."""
    try:
        print_status(f"\nCreating template: {name}", 'info')
        
        templates_dir = BASE_DIR / 'templates' / 'email'
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Save HTML template
        html_file = templates_dir / f"{name}.html"
        html_file.write_text(html_content)
        
        # Save text template
        text_file = templates_dir / f"{name}.txt"
        text_file.write_text(text_content)
        
        # Save metadata
        metadata_file = templates_dir / f"{name}.json"
        metadata = {
            'subject': subject,
            'created_at': datetime.now().isoformat(),
            'variables': re.findall(r'\{\{\s*(\w+)\s*\}\}', html_content)
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        print_status("✓ Template created successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error creating template: {e}", 'error')


def list_templates() -> None:
    """List all available email templates."""
    print_status("\nListing email templates:", 'info')
    
    templates_dir = BASE_DIR / 'templates' / 'email'
    if not templates_dir.exists():
        print_status("No templates directory found", 'warning')
        return
    
    for metadata_file in templates_dir.glob('*.json'):
        name = metadata_file.stem
        try:
            metadata = json.loads(metadata_file.read_text())
            print(f"\nTemplate: {name}")
            print(f"Subject: {metadata['subject']}")
            print(f"Variables: {', '.join(metadata['variables'])}")
            print(f"Created: {metadata['created_at']}")
        except Exception:
            print(f"Error reading template: {name}")


def preview_template(name: str, context: Optional[Dict] = None) -> None:
    """Preview an email template with optional context."""
    try:
        print_status(f"\nPreviewing template: {name}", 'info')
        
        templates_dir = BASE_DIR / 'templates' / 'email'
        html_file = templates_dir / f"{name}.html"
        text_file = templates_dir / f"{name}.txt"
        metadata_file = templates_dir / f"{name}.json"
        
        if not all(f.exists() for f in [html_file, text_file, metadata_file]):
            print_status("✗ Template files not found", 'error')
            return
        
        # Load metadata
        metadata = json.loads(metadata_file.read_text())
        
        # Create sample context if not provided
        if not context:
            context = {var: f"[{var}]" for var in metadata['variables']}
        
        # Render templates
        html_content = Template(html_file.read_text()).render(Context(context))
        text_content = Template(text_file.read_text()).render(Context(context))
        
        print("\nSubject:")
        print(Template(metadata['subject']).render(Context(context)))
        
        print("\nText Version:")
        print("-" * 40)
        print(text_content)
        
        print("\nHTML Version:")
        print("-" * 40)
        print(html_content)
    
    except Exception as e:
        print_status(f"✗ Error previewing template: {e}", 'error')


def send_test_email(template_name: str, to_email: str, context: Optional[Dict] = None) -> None:
    """Send a test email using a template."""
    try:
        print_status(f"\nSending test email to {to_email}", 'info')
        
        templates_dir = BASE_DIR / 'templates' / 'email'
        metadata_file = templates_dir / f"{template_name}.json"
        
        if not metadata_file.exists():
            print_status("✗ Template not found", 'error')
            return
        
        # Load metadata
        metadata = json.loads(metadata_file.read_text())
        
        # Create sample context if not provided
        if not context:
            context = {var: f"[{var}]" for var in metadata['variables']}
        
        # Render email
        subject = Template(metadata['subject']).render(Context(context))
        html_message = render_to_string(f"email/{template_name}.html", context)
        text_message = render_to_string(f"email/{template_name}.txt", context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False
        )
        
        print_status("✓ Test email sent successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error sending test email: {e}", 'error')


def validate_templates() -> None:
    """Validate all email templates."""
    print_status("\nValidating email templates:", 'info')
    
    templates_dir = BASE_DIR / 'templates' / 'email'
    if not templates_dir.exists():
        print_status("No templates directory found", 'warning')
        return
    
    issues_found = False
    
    for metadata_file in templates_dir.glob('*.json'):
        name = metadata_file.stem
        print(f"\nChecking {name}...")
        
        try:
            # Check files exist
            html_file = templates_dir / f"{name}.html"
            text_file = templates_dir / f"{name}.txt"
            
            if not html_file.exists():
                print_status(f"! Missing HTML template: {name}.html", 'warning')
                issues_found = True
            
            if not text_file.exists():
                print_status(f"! Missing text template: {name}.txt", 'warning')
                issues_found = True
            
            # Load and validate metadata
            metadata = json.loads(metadata_file.read_text())
            required_fields = {'subject', 'created_at', 'variables'}
            missing_fields = required_fields - set(metadata.keys())
            
            if missing_fields:
                print_status(f"! Missing metadata fields: {', '.join(missing_fields)}", 'warning')
                issues_found = True
            
            # Validate templates
            if html_file.exists() and text_file.exists():
                # Create test context
                context = {var: f"test_{var}" for var in metadata['variables']}
                
                # Try rendering templates
                try:
                    Template(html_file.read_text()).render(Context(context))
                    Template(text_file.read_text()).render(Context(context))
                except Exception as e:
                    print_status(f"! Template rendering error: {e}", 'warning')
                    issues_found = True
        
        except Exception as e:
            print_status(f"✗ Error validating template {name}: {e}", 'error')
            issues_found = True
    
    if not issues_found:

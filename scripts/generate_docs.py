#!/usr/bin/env python
"""
Script to generate API documentation from Django views and models.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import django
from django.urls import URLPattern, URLResolver, get_resolver
from django.utils.module_loading import import_string
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


def get_view_docs(view_class: Any) -> Dict[str, Any]:
    """Extract documentation from a view class."""
    docs = {
        'description': view_class.__doc__ or 'No description provided',
        'methods': [],
        'fields': [],
        'permissions': [],
        'parameters': [],
        'responses': []
    }

    # Get supported methods
    if hasattr(view_class, 'http_method_names'):
        docs['methods'] = [method.upper() for method in view_class.http_method_names if method != 'options']

    # Get serializer fields
    if hasattr(view_class, 'serializer_class'):
        serializer = view_class.serializer_class()
        docs['fields'] = [
            {
                'name': name,
                'type': field.__class__.__name__,
                'required': field.required,
                'help_text': field.help_text
            }
            for name, field in serializer.fields.items()
        ]

    # Get permissions
    if hasattr(view_class, 'permission_classes'):
        docs['permissions'] = [
            perm.__name__ for perm in view_class.permission_classes
        ]

    # Get query parameters
    if hasattr(view_class, 'filterset_class'):
        docs['parameters'] = [
            {
                'name': name,
                'type': field.__class__.__name__,
                'required': field.required if hasattr(field, 'required') else False,
                'help_text': field.help_text if hasattr(field, 'help_text') else None
            }
            for name, field in view_class.filterset_class.base_filters.items()
        ]

    # Get response formats
    if hasattr(view_class, 'get_serializer_class'):
        try:
            serializer = view_class.get_serializer_class()()
            docs['responses'] = {
                '200': {
                    'description': 'Successful response',
                    'content': serializer.data
                }
            }
        except Exception:
            pass

    return docs


def get_model_docs(model_class: Any) -> Dict[str, Any]:
    """Extract documentation from a model class."""
    docs = {
        'name': model_class.__name__,
        'description': model_class.__doc__ or 'No description provided',
        'fields': [],
        'relationships': [],
        'meta': {}
    }

    # Get model fields
    for field in model_class._meta.fields:
        field_info = {
            'name': field.name,
            'type': field.__class__.__name__,
            'null': field.null,
            'blank': field.blank,
            'help_text': str(field.help_text) if field.help_text else None
        }
        docs['fields'].append(field_info)

    # Get relationships
    for field in model_class._meta.related_objects:
        rel_info = {
            'name': field.name,
            'type': field.__class__.__name__,
            'model': field.related_model.__name__,
            'related_name': field.remote_field.related_name
        }
        docs['relationships'].append(rel_info)

    # Get meta options
    if hasattr(model_class, '_meta'):
        meta = model_class._meta
        docs['meta'] = {
            'verbose_name': str(meta.verbose_name),
            'verbose_name_plural': str(meta.verbose_name_plural),
            'ordering': meta.ordering,
            'unique_together': meta.unique_together,
            'indexes': [str(idx) for idx in meta.indexes]
        }

    return docs


def get_urls(urlpatterns: List[Any], prefix: str = '') -> List[Dict[str, Any]]:
    """Recursively extract URL patterns and their documentation."""
    urls = []

    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # Recursively process URL patterns
            urls.extend(get_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
        elif isinstance(pattern, URLPattern):
            # Get view class
            if hasattr(pattern.callback, 'view_class'):
                view_class = pattern.callback.view_class
            elif hasattr(pattern.callback, '__name__'):
                try:
                    view_class = import_string(pattern.callback.__module__ + '.' + pattern.callback.__name__)
                except ImportError:
                    continue
            else:
                continue

            # Get documentation
            url_info = {
                'path': prefix + str(pattern.pattern),
                'name': pattern.name,
                'view': view_class.__name__,
                'docs': get_view_docs(view_class)
            }
            urls.append(url_info)

    return urls


def generate_markdown(urls: List[Dict[str, Any]], models: Dict[str, Any]) -> str:
    """Generate markdown documentation."""
    md = "# healmymind API Documentation\n\n"

    # Table of Contents
    md += "## Table of Contents\n\n"
    md += "- [API Endpoints](#api-endpoints)\n"
    md += "- [Models](#models)\n"
    md += "- [Authentication](#authentication)\n"
    md += "- [Error Handling](#error-handling)\n\n"

    # API Endpoints
    md += "## API Endpoints\n\n"
    for url in urls:
        md += f"### {url['view']}\n\n"
        md += f"**Path:** `{url['path']}`\n\n"
        if url['name']:
            md += f"**Name:** `{url['name']}`\n\n"

        docs = url['docs']
        md += f"{docs['description']}\n\n"

        if docs['methods']:
            md += "**Methods:**\n"
            for method in docs['methods']:
                md += f"- `{method}`\n"
            md += "\n"

        if docs['permissions']:
            md += "**Permissions:**\n"
            for perm in docs['permissions']:
                md += f"- {perm}\n"
            md += "\n"

        if docs['fields']:
            md += "**Fields:**\n"
            for field in docs['fields']:
                required = "required" if field['required'] else "optional"
                md += f"- `{field['name']}` ({field['type']}, {required})"
                if field['help_text']:
                    md += f": {field['help_text']}"
                md += "\n"
            md += "\n"

        if docs['parameters']:
            md += "**Query Parameters:**\n"
            for param in docs['parameters']:
                required = "required" if param['required'] else "optional"
                md += f"- `{param['name']}` ({param['type']}, {required})"
                if param['help_text']:
                    md += f": {param['help_text']}"
                md += "\n"
            md += "\n"

    # Models
    md += "## Models\n\n"
    for model_name, model_docs in models.items():
        md += f"### {model_name}\n\n"
        md += f"{model_docs['description']}\n\n"

        if model_docs['fields']:
            md += "**Fields:**\n"
            for field in model_docs['fields']:
                nullable = "nullable" if field['null'] else "not nullable"
                md += f"- `{field['name']}` ({field['type']}, {nullable})"
                if field['help_text']:
                    md += f": {field['help_text']}"
                md += "\n"
            md += "\n"

        if model_docs['relationships']:
            md += "**Relationships:**\n"
            for rel in model_docs['relationships']:
                md += f"- `{rel['name']}` ({rel['type']} to {rel['model']})"
                if rel['related_name']:
                    md += f", related_name: `{rel['related_name']}`"
                md += "\n"
            md += "\n"

    # Authentication
    md += "## Authentication\n\n"
    md += "This API uses JWT (JSON Web Token) authentication.\n\n"
    md += "To authenticate, include the JWT token in the Authorization header:\n"
    md += "```http\nAuthorization: Bearer <token>\n```\n\n"

    # Error Handling
    md += "## Error Handling\n\n"
    md += "The API uses standard HTTP response codes:\n\n"
    md += "- `200 OK`: Request successful\n"
    md += "- `201 Created`: Resource created successfully\n"
    md += "- `400 Bad Request`: Invalid request\n"
    md += "- `401 Unauthorized`: Authentication required\n"
    md += "- `403 Forbidden`: Permission denied\n"
    md += "- `404 Not Found`: Resource not found\n"
    md += "- `500 Internal Server Error`: Server error\n\n"

    return md


def main() -> None:
    """Main function to generate API documentation."""
    try:
        print_status("\nGenerating API documentation...", 'info')

        # Get URL patterns
        resolver = get_resolver()
        urls = get_urls(resolver.url_patterns)

        # Get models
        models = {}
        for app_config in django.apps.apps.get_app_configs():
            for model in app_config.get_models():
                models[model.__name__] = get_model_docs(model)

        # Generate markdown
        docs_dir = BASE_DIR / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        md = generate_markdown(urls, models)
        
        with open(docs_dir / 'api.md', 'w') as f:
            f.write(md)

        print_status("✓ Documentation generated successfully", 'success')
        print_status(f"Documentation saved to: {docs_dir / 'api.md'}", 'info')

    except Exception as e:
        print_status(f"✗ Error generating documentation: {e}", 'error')
        sys.exit(1)


if __name__ == '__main__':
    main()

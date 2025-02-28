#!/usr/bin/env python
"""
Script to manage translations and internationalization.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import django
import polib
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


def extract_messages() -> None:
    """Extract messages for translation."""
    try:
        print_status("\nExtracting messages for translation...", 'info')
        
        # Make messages for Python files
        call_command('makemessages', all=True, ignore=['venv/*', 'node_modules/*'])
        
        # Make messages for JavaScript files
        call_command('makemessages', all=True, domain='djangojs', ignore=['venv/*', 'node_modules/*'])
        
        print_status("✓ Messages extracted successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error extracting messages: {e}", 'error')
        sys.exit(1)


def compile_messages() -> None:
    """Compile translation messages."""
    try:
        print_status("\nCompiling translation messages...", 'info')
        
        call_command('compilemessages')
        
        print_status("✓ Messages compiled successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error compiling messages: {e}", 'error')
        sys.exit(1)


def check_translations() -> None:
    """Check translation files for issues."""
    print_status("\nChecking translation files...", 'info')
    
    locale_dir = BASE_DIR / 'locale'
    if not locale_dir.exists():
        print_status("✗ No locale directory found", 'error')
        return
    
    issues_found = False
    
    for po_file in locale_dir.rglob('*.po'):
        print(f"\nChecking {po_file.relative_to(BASE_DIR)}...")
        
        po = polib.pofile(str(po_file))
        
        # Check for untranslated messages
        untranslated = [entry for entry in po if not entry.translated()]
        if untranslated:
            issues_found = True
            print_status(f"! Found {len(untranslated)} untranslated messages:", 'warning')
            for entry in untranslated:
                print(f"  - {entry.msgid}")
        
        # Check for fuzzy translations
        fuzzy = [entry for entry in po if 'fuzzy' in entry.flags]
        if fuzzy:
            issues_found = True
            print_status(f"! Found {len(fuzzy)} fuzzy translations:", 'warning')
            for entry in fuzzy:
                print(f"  - {entry.msgid}")
    
    if not issues_found:
        print_status("✓ No translation issues found", 'success')


def update_translations(language: str) -> None:
    """Update translation files for a specific language."""
    try:
        print_status(f"\nUpdating translations for {language}...", 'info')
        
        # Create locale directory if it doesn't exist
        locale_dir = BASE_DIR / 'locale' / language / 'LC_MESSAGES'
        locale_dir.mkdir(parents=True, exist_ok=True)
        
        # Make messages for the language
        call_command('makemessages', locale=[language], ignore=['venv/*', 'node_modules/*'])
        call_command('makemessages', locale=[language], domain='djangojs', ignore=['venv/*', 'node_modules/*'])
        
        print_status("✓ Translation files updated successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error updating translations: {e}", 'error')
        sys.exit(1)


def sync_translations() -> None:
    """Synchronize translations across all languages."""
    try:
        print_status("\nSynchronizing translations...", 'info')
        
        # Get all language codes
        languages = [d.name for d in (BASE_DIR / 'locale').iterdir() if d.is_dir()]
        
        # Extract base messages
        extract_messages()
        
        # Update each language
        for language in languages:
            update_translations(language)
        
        # Compile messages
        compile_messages()
        
        print_status("✓ Translations synchronized successfully", 'success')
    
    except Exception as e:
        print_status(f"✗ Error synchronizing translations: {e}", 'error')
        sys.exit(1)


def export_translations(language: str, output_file: str) -> None:
    """Export translations to JSON format."""
    try:
        print_status(f"\nExporting translations for {language}...", 'info')
        
        translations = {}
        po_file = BASE_DIR / 'locale' / language / 'LC_MESSAGES' / 'django.po'
        
        if po_file.exists():
            po = polib.pofile(str(po_file))
            for entry in po:
                if entry.translated():
                    translations[entry.msgid] = entry.msgstr
        
        # Export to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        
        print_status(f"✓ Translations exported to {output_file}", 'success')
    
    except Exception as e:
        print_status(f"✗ Error exporting translations: {e}", 'error')
        sys.exit(1)


def import_translations(language: str, input_file: str) -> None:
    """Import translations from JSON format."""
    try:
        print_status(f"\nImporting translations for {language}...", 'info')
        
        # Read JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        po_file = BASE_DIR / 'locale' / language / 'LC_MESSAGES' / 'django.po'
        
        if po_file.exists():
            po = polib.pofile(str(po_file))
            
            # Update translations
            for entry in po:
                if entry.msgid in translations:
                    entry.msgstr = translations[entry.msgid]
            
            # Save changes
            po.save()
            
            # Compile messages
            compile_messages()
            
            print_status("✓ Translations imported successfully", 'success')
        else:
            print_status(f"✗ No .po file found for language {language}", 'error')
    
    except Exception as e:
        print_status(f"✗ Error importing translations: {e}", 'error')
        sys.exit(1)


def generate_stats() -> None:
    """Generate translation statistics."""
    print_status("\nGenerating translation statistics...", 'info')
    
    locale_dir = BASE_DIR / 'locale'
    if not locale_dir.exists():
        print_status("✗ No locale directory found", 'error')
        return
    
    stats = {}
    
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            language = lang_dir.name
            po_file = lang_dir / 'LC_MESSAGES' / 'django.po'
            
            if po_file.exists():
                po = polib.pofile(str(po_file))
                stats[language] = {
                    'total': len(po),
                    'translated': len(po.translated_entries()),
                    'fuzzy': len(po.fuzzy_entries()),
                    'obsolete': len(po.obsolete_entries()),
                    'percent_translated': po.percent_translated()
                }
    
    # Print statistics
    for language, data in stats.items():
        print(f"\nLanguage: {language}")
        print(f"Total messages: {data['total']}")
        print(f"Translated: {data['translated']}")
        print(f"Fuzzy: {data['fuzzy']}")
        print(f"Obsolete: {data['obsolete']}")
        print(f"Percent translated: {data['percent_translated']}%")


def main() -> None:
    """Main function to manage translations."""
    import argparse

    parser = argparse.ArgumentParser(description='Translation management script')
    parser.add_argument('--extract', action='store_true', help='Extract messages')
    parser.add_argument('--compile', action='store_true', help='Compile messages')
    parser.add_argument('--check', action='store_true', help='Check translations')
    parser.add_argument('--update', help='Update translations for language')
    parser.add_argument('--sync', action='store_true', help='Synchronize all translations')
    parser.add_argument('--export', nargs=2, metavar=('LANG', 'FILE'), help='Export translations to JSON')
    parser.add_argument('--import', nargs=2, metavar=('LANG', 'FILE'), help='Import translations from JSON')
    parser.add_argument('--stats', action='store_true', help='Generate translation statistics')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.extract:
        extract_messages()

    if args.compile:
        compile_messages()

    if args.check:
        check_translations()

    if args.update:
        update_translations(args.update)

    if args.sync:
        sync_translations()

    if args.export:
        export_translations(args.export[0], args.export[1])

    if getattr(args, 'import'):
        import_translations(getattr(args, 'import')[0], getattr(args, 'import')[1])

    if args.stats:
        generate_stats()


if __name__ == '__main__':
    main()

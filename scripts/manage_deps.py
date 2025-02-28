#!/usr/bin/env python
"""
Script to manage Python dependencies and keep them up to date.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pkg_resources
import requests
from termcolor import colored

# Constants
PYPI_URL = "https://pypi.org/pypi/{package}/json"
REQUIREMENTS_FILE = "requirements.txt"
POETRY_FILE = "pyproject.toml"


def print_status(message: str, status: str = 'info') -> None:
    """Print colored status messages."""
    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan'
    }
    print(colored(message, colors.get(status, 'white')))


def get_installed_packages() -> Dict[str, str]:
    """Get currently installed packages and their versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}


def get_latest_version(package: str) -> Optional[str]:
    """Get the latest version of a package from PyPI."""
    try:
        response = requests.get(PYPI_URL.format(package=package))
        response.raise_for_status()
        return response.json()['info']['version']
    except Exception:
        return None


def parse_requirements(filename: str = REQUIREMENTS_FILE) -> List[Tuple[str, str]]:
    """Parse requirements.txt file."""
    requirements = []
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('==')
                    if len(parts) == 2:
                        requirements.append((parts[0], parts[1]))
                    else:
                        requirements.append((line, ''))
        return requirements
    except FileNotFoundError:
        return []


def check_updates() -> List[Tuple[str, str, str]]:
    """Check for available package updates."""
    updates = []
    installed = get_installed_packages()

    print_status("\nChecking for package updates...", 'info')
    for package, current_version in installed.items():
        latest_version = get_latest_version(package)
        if latest_version and latest_version != current_version:
            updates.append((package, current_version, latest_version))

    return updates


def update_packages(packages: Optional[List[str]] = None) -> None:
    """Update specified packages or all packages."""
    try:
        if packages:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages
        else:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', REQUIREMENTS_FILE]

        subprocess.run(cmd, check=True)
        print_status("✓ Packages updated successfully", 'success')
    except subprocess.CalledProcessError as e:
        print_status(f"✗ Error updating packages: {e}", 'error')
        sys.exit(1)


def check_security() -> None:
    """Check for known security vulnerabilities."""
    try:
        print_status("\nChecking for security vulnerabilities...", 'info')
        result = subprocess.run(['safety', 'check'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("✓ No known vulnerabilities found", 'success')
        else:
            print_status("! Security vulnerabilities found:", 'warning')
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print_status(f"✗ Error checking security: {e}", 'error')


def generate_requirements() -> None:
    """Generate requirements.txt from installed packages."""
    try:
        print_status("\nGenerating requirements.txt...", 'info')
        cmd = [sys.executable, '-m', 'pip', 'freeze']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        with open(REQUIREMENTS_FILE, 'w') as f:
            f.write(result.stdout)
        
        print_status("✓ Requirements file generated successfully", 'success')
    except Exception as e:
        print_status(f"✗ Error generating requirements: {e}", 'error')
        sys.exit(1)


def sync_poetry() -> None:
    """Sync requirements.txt with pyproject.toml."""
    try:
        print_status("\nSyncing dependencies with Poetry...", 'info')
        
        # Export requirements from Poetry
        subprocess.run(['poetry', 'export', '-f', 'requirements.txt', '--output', REQUIREMENTS_FILE], check=True)
        
        # Install requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE], check=True)
        
        print_status("✓ Dependencies synced successfully", 'success')
    except subprocess.CalledProcessError as e:
        print_status(f"✗ Error syncing dependencies: {e}", 'error')
        sys.exit(1)


def clean_unused() -> None:
    """Remove unused dependencies."""
    try:
        print_status("\nCleaning unused dependencies...", 'info')
        
        # Find unused imports
        subprocess.run(['autoflake', '--recursive', '--remove-all-unused-imports', '.'], check=True)
        
        # Generate new requirements
        generate_requirements()
        
        print_status("✓ Unused dependencies cleaned successfully", 'success')
    except subprocess.CalledProcessError as e:
        print_status(f"✗ Error cleaning dependencies: {e}", 'error')
        sys.exit(1)


def create_dependency_graph() -> None:
    """Create a dependency graph visualization."""
    try:
        print_status("\nGenerating dependency graph...", 'info')
        
        # Create docs directory if it doesn't exist
        Path('docs').mkdir(exist_ok=True)
        
        # Generate graph using pipdeptree
        cmd = ['pipdeptree', '--graph-output', 'dot']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Save dot file
        dot_file = 'docs/dependencies.dot'
        with open(dot_file, 'w') as f:
            f.write(result.stdout)
        
        # Convert to PNG if graphviz is installed
        try:
            subprocess.run(['dot', '-Tpng', dot_file, '-o', 'docs/dependencies.png'], check=True)
            print_status("✓ Dependency graph generated: docs/dependencies.png", 'success')
        except subprocess.CalledProcessError:
            print_status("! Graphviz not installed. Dot file generated: " + dot_file, 'warning')
            
    except subprocess.CalledProcessError as e:
        print_status(f"✗ Error generating dependency graph: {e}", 'error')
        sys.exit(1)


def main() -> None:
    """Main function to manage dependencies."""
    import argparse

    parser = argparse.ArgumentParser(description='Dependency management script')
    parser.add_argument('--check', action='store_true', help='Check for updates')
    parser.add_argument('--update', nargs='*', help='Update all or specified packages')
    parser.add_argument('--security', action='store_true', help='Check for security vulnerabilities')
    parser.add_argument('--generate', action='store_true', help='Generate requirements.txt')
    parser.add_argument('--sync', action='store_true', help='Sync with Poetry')
    parser.add_argument('--clean', action='store_true', help='Clean unused dependencies')
    parser.add_argument('--graph', action='store_true', help='Generate dependency graph')
    parser.add_argument('--all', action='store_true', help='Run all checks')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.check or args.all:
        updates = check_updates()
        if updates:
            print_status("\nUpdates available:", 'warning')
            for package, current, latest in updates:
                print(f"  {package}: {current} → {latest}")
        else:
            print_status("✓ All packages are up to date", 'success')

    if args.update is not None:
        update_packages(args.update)

    if args.security or args.all:
        check_security()

    if args.generate or args.all:
        generate_requirements()

    if args.sync or args.all:
        sync_poetry()

    if args.clean or args.all:
        clean_unused()

    if args.graph or args.all:
        create_dependency_graph()


if __name__ == '__main__':
    main()

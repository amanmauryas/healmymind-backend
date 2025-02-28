#!/usr/bin/env python
"""
Script to run code quality checks and linting.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from termcolor import colored

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


def print_status(message: str, status: str = 'info') -> None:
    """Print colored status messages."""
    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan'
    }
    print(colored(message, colors.get(status, 'white')))


def run_command(command: List[str], fix: bool = False) -> Tuple[int, str]:
    """Run a command and return exit code and output."""
    try:
        if fix:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout + e.stderr


def check_black(fix: bool = False) -> bool:
    """Run Black code formatter."""
    print_status("\nRunning Black code formatter...", 'info')
    
    command = ['black', '.']
    if not fix:
        command.append('--check')
    
    exit_code, output = run_command(command)
    
    if exit_code == 0:
        print_status("✓ Black check passed", 'success')
        return True
    else:
        print_status("✗ Black check failed", 'error')
        print(output)
        return False


def check_isort(fix: bool = False) -> bool:
    """Run isort import sorter."""
    print_status("\nRunning isort import sorter...", 'info')
    
    command = ['isort', '.']
    if not fix:
        command.append('--check-only')
        command.append('--diff')
    
    exit_code, output = run_command(command)
    
    if exit_code == 0:
        print_status("✓ isort check passed", 'success')
        return True
    else:
        print_status("✗ isort check failed", 'error')
        print(output)
        return False


def check_flake8() -> bool:
    """Run Flake8 linter."""
    print_status("\nRunning Flake8 linter...", 'info')
    
    exit_code, output = run_command(['flake8', '.'])
    
    if exit_code == 0:
        print_status("✓ Flake8 check passed", 'success')
        return True
    else:
        print_status("✗ Flake8 check failed", 'error')
        print(output)
        return False


def check_mypy() -> bool:
    """Run MyPy type checker."""
    print_status("\nRunning MyPy type checker...", 'info')
    
    exit_code, output = run_command(['mypy', '.'])
    
    if exit_code == 0:
        print_status("✓ MyPy check passed", 'success')
        return True
    else:
        print_status("✗ MyPy check failed", 'error')
        print(output)
        return False


def check_pylint() -> bool:
    """Run Pylint code analyzer."""
    print_status("\nRunning Pylint code analyzer...", 'info')
    
    exit_code, output = run_command(['pylint', '.'])
    
    if exit_code == 0:
        print_status("✓ Pylint check passed", 'success')
        return True
    else:
        print_status("✗ Pylint check failed", 'error')
        print(output)
        return False


def check_bandit() -> bool:
    """Run Bandit security checker."""
    print_status("\nRunning Bandit security checker...", 'info')
    
    exit_code, output = run_command(['bandit', '-r', '.', '-x', 'tests,venv'])
    
    if exit_code == 0:
        print_status("✓ Bandit check passed", 'success')
        return True
    else:
        print_status("✗ Bandit check failed", 'error')
        print(output)
        return False


def check_docstrings() -> bool:
    """Run pydocstyle docstring checker."""
    print_status("\nRunning pydocstyle docstring checker...", 'info')
    
    exit_code, output = run_command(['pydocstyle', '.'])
    
    if exit_code == 0:
        print_status("✓ Docstring check passed", 'success')
        return True
    else:
        print_status("✗ Docstring check failed", 'error')
        print(output)
        return False


def check_complexity() -> bool:
    """Run Radon code complexity checker."""
    print_status("\nRunning Radon code complexity checker...", 'info')
    
    # Check cyclomatic complexity
    print("\nCyclomatic Complexity:")
    cc_code, cc_output = run_command(['radon', 'cc', '.', '--min', 'C'])
    print(cc_output)
    
    # Check maintainability index
    print("\nMaintainability Index:")
    mi_code, mi_output = run_command(['radon', 'mi', '.', '--min', 'B'])
    print(mi_output)
    
    if cc_code == 0 and mi_code == 0:
        print_status("✓ Complexity check passed", 'success')
        return True
    else:
        print_status("✗ Complexity check failed", 'error')
        return False


def check_dead_code() -> bool:
    """Run Vulture dead code detector."""
    print_status("\nRunning Vulture dead code detector...", 'info')
    
    exit_code, output = run_command(['vulture', '.'])
    
    if exit_code == 0:
        print_status("✓ Dead code check passed", 'success')
        return True
    else:
        print_status("! Potential dead code found", 'warning')
        print(output)
        return False


def generate_reports() -> None:
    """Generate code quality reports."""
    print_status("\nGenerating code quality reports...", 'info')
    
    reports_dir = BASE_DIR / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    # Pylint report
    run_command(['pylint', '.', '--output', str(reports_dir / 'pylint_report.txt')])
    
    # Coverage report
    run_command(['coverage', 'run', '-m', 'pytest'])
    run_command(['coverage', 'html', '-d', str(reports_dir / 'coverage')])
    
    # Complexity report
    run_command(['radon', 'cc', '.', '--xml', '>', str(reports_dir / 'complexity.xml')])
    
    print_status(f"✓ Reports generated in {reports_dir}", 'success')


def main() -> None:
    """Main function to run code quality checks."""
    import argparse

    parser = argparse.ArgumentParser(description='Code quality check script')
    parser.add_argument('--fix', action='store_true', help='Fix issues where possible')
    parser.add_argument('--black', action='store_true', help='Run Black formatter')
    parser.add_argument('--isort', action='store_true', help='Run isort')
    parser.add_argument('--flake8', action='store_true', help='Run Flake8')
    parser.add_argument('--mypy', action='store_true', help='Run MyPy')
    parser.add_argument('--pylint', action='store_true', help='Run Pylint')
    parser.add_argument('--bandit', action='store_true', help='Run Bandit')
    parser.add_argument('--docstrings', action='store_true', help='Check docstrings')
    parser.add_argument('--complexity', action='store_true', help='Check complexity')
    parser.add_argument('--dead-code', action='store_true', help='Check for dead code')
    parser.add_argument('--reports', action='store_true', help='Generate reports')
    parser.add_argument('--all', action='store_true', help='Run all checks')

    args = parser.parse_args()

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    success = True

    if args.black or args.all:
        success &= check_black(args.fix)

    if args.isort or args.all:
        success &= check_isort(args.fix)

    if args.flake8 or args.all:
        success &= check_flake8()

    if args.mypy or args.all:
        success &= check_mypy()

    if args.pylint or args.all:
        success &= check_pylint()

    if args.bandit or args.all:
        success &= check_bandit()

    if args.docstrings or args.all:
        success &= check_docstrings()

    if args.complexity or args.all:
        success &= check_complexity()

    if args.dead_code or args.all:
        success &= check_dead_code()

    if args.reports or args.all:
        generate_reports()

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()

# Contributing to healmymind Backend

First off, thank you for considering contributing to healmymind! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Security](#security)

## Code of Conduct

### Our Pledge
We are committed to providing a friendly, safe, and welcoming environment for all contributors.

### Our Standards
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Enforcement
Violations of the code of conduct may result in temporary or permanent exclusion from the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/healmymind.git
cd healmymind/backend
```

3. Set up development environment:
```bash
# Windows
run.bat init

# Unix/Linux/macOS
./run.sh init
```

4. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

## Development Process

### 1. Pick an Issue
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it
- Ask questions if anything is unclear

### 2. Local Development
```bash
# Start development server
./run.sh manage runserver

# Run tests while developing
./run.sh test --watch
```

### 3. Keep Your Branch Updated
```bash
git fetch origin
git rebase origin/main
```

## Pull Request Process

1. Update Documentation
- Add docstrings to new functions/classes
- Update README.md if needed
- Add migration notes if required

2. Run Tests and Checks
```bash
# Run all checks
./run.sh test all
```

3. Create Pull Request
- Use a clear, descriptive title
- Reference related issues
- Describe your changes in detail
- Add screenshots for UI changes

4. Code Review
- Address review comments
- Keep discussions focused and professional
- Update your branch if needed

## Coding Standards

### Python Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

### Example
```python
from typing import List, Optional

def process_user_data(user_id: int, data: dict) -> Optional[List[dict]]:
    """
    Process user data and return formatted results.
    
    Args:
        user_id: The ID of the user
        data: Dictionary containing user data
        
    Returns:
        List of processed data dictionaries or None if processing fails
    """
    if not data:
        return None
    
    return [
        {
            'id': user_id,
            'field': value,
            'processed_at': timezone.now()
        }
        for field, value in data.items()
    ]
```

### Code Organization
- Group related functionality
- Use meaningful file names
- Keep files focused and manageable

## Testing Guidelines

### Test Structure
```python
from django.test import TestCase

class UserTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create(
            email='test@example.com',
            username='testuser'
        )

    def test_user_creation(self):
        """Test user creation and validation."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
```

### Test Coverage
- Aim for 90%+ coverage
- Test edge cases
- Include integration tests

## Documentation

### Docstring Format
```python
def function_name(param1: type1, param2: type2) -> return_type:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when this exception occurs
    """
```

### API Documentation
- Use OpenAPI/Swagger annotations
- Include request/response examples
- Document error responses

## Security

### Guidelines
- Never commit sensitive data
- Use environment variables for secrets
- Follow security best practices
- Report security issues privately

### Security Checks
```bash
# Run security checks
./run.sh test security
```

## Commit Messages

### Format
```
type(scope): Brief description

Detailed description of changes
```

### Types
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Example
```
feat(auth): Add password reset functionality

- Add password reset endpoints
- Implement email notification
- Add password reset templates
- Update documentation
```

## Release Process

1. Version Bump
```bash
./run.sh manage version bump
```

2. Update Changelog
- Add new version section
- List all changes
- Credit contributors

3. Create Release
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Questions?

- Check existing documentation
- Ask in GitHub Discussions
- Join our Discord server
- Email: dev@healmymindai.com

Thank you for contributing to healmymind! 🚀

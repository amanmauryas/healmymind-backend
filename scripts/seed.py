#!/usr/bin/env python
"""
Script to seed the database with initial data.
"""
import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.core.management import call_command
from django.db import transaction

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')
django.setup()

# Import models after Django setup
from blog.models import Category, Post, Tag  # noqa: E402
from chat.models import SupportResource  # noqa: E402
from tests.models import Test, Question, Option, ScoringRange  # noqa: E402
from users.models import User  # noqa: E402


def create_superuser():
    """Create a superuser if it doesn't exist."""
    try:
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@healmymindai.com',
                password='admin123'  # Change this in production
            )
            print("✓ Superuser created")
        else:
            print("✓ Superuser already exists")
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")


def create_test_data():
    """Create initial test data."""
    try:
        # PHQ-9 Depression Test
        phq9, _ = Test.objects.get_or_create(
            name="PHQ-9 Depression Screening",
            test_type="PHQ9",
            defaults={
                'description': "Patient Health Questionnaire-9",
                'instructions': "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
                'estimated_time': 5
            }
        )

        # PHQ-9 Questions
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself",
            "Trouble concentrating on things",
            "Moving or speaking so slowly that other people could have noticed",
            "Thoughts that you would be better off dead or of hurting yourself"
        ]

        for i, text in enumerate(questions, 1):
            question, _ = Question.objects.get_or_create(
                test=phq9,
                order=i,
                defaults={'text': text}
            )

            # Options for each question
            options = [
                ("Not at all", 0),
                ("Several days", 1),
                ("More than half the days", 2),
                ("Nearly every day", 3)
            ]

            for j, (text, value) in enumerate(options, 1):
                Option.objects.get_or_create(
                    question=question,
                    order=j,
                    defaults={
                        'text': text,
                        'value': value
                    }
                )

        # Scoring ranges
        ranges = [
            (0, 4, "MINIMAL", "Minimal depression"),
            (5, 9, "MILD", "Mild depression"),
            (10, 14, "MODERATE", "Moderate depression"),
            (15, 27, "SEVERE", "Severe depression")
        ]

        for min_score, max_score, severity, description in ranges:
            ScoringRange.objects.get_or_create(
                test=phq9,
                min_score=min_score,
                max_score=max_score,
                defaults={
                    'severity': severity,
                    'description': description
                }
            )

        print("✓ Test data created")
    except Exception as e:
        print(f"✗ Error creating test data: {e}")


def create_blog_data():
    """Create initial blog data."""
    try:
        # Categories
        categories = [
            ("Mental Health", "Articles about mental health and well-being"),
            ("Self Care", "Tips and strategies for self-care"),
            ("Research", "Latest mental health research and findings"),
            ("Resources", "Mental health resources and support"),
        ]

        for name, description in categories:
            Category.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'slug': name.lower().replace(' ', '-')
                }
            )

        # Tags
        tags = [
            "anxiety", "depression", "stress", "mindfulness",
            "therapy", "self-help", "mental-health", "wellness"
        ]

        for name in tags:
            Tag.objects.get_or_create(
                name=name,
                defaults={'slug': name}
            )

        print("✓ Blog data created")
    except Exception as e:
        print(f"✗ Error creating blog data: {e}")


def create_support_resources():
    """Create initial support resources."""
    try:
        resources = [
            {
                'title': "National Suicide Prevention Lifeline",
                'description': "24/7, free and confidential support",
                'resource_type': "CRISIS",
                'phone_number': "988",
                'is_emergency': True,
                'order': 1
            },
            {
                'title': "Crisis Text Line",
                'description': "Text HOME to 741741",
                'resource_type': "CRISIS",
                'is_emergency': True,
                'order': 2
            },
            {
                'title': "Find a Therapist",
                'description': "Search for licensed therapists",
                'resource_type': "THERAPY",
                'url': "https://www.psychologytoday.com/us/therapists",
                'order': 3
            }
        ]

        for resource in resources:
            SupportResource.objects.get_or_create(
                title=resource['title'],
                defaults=resource
            )

        print("✓ Support resources created")
    except Exception as e:
        print(f"✗ Error creating support resources: {e}")


@transaction.atomic
def main():
    """Main function to seed the database."""
    print("\nSeeding database...\n")

    # Run migrations first
    print("Running migrations...")
    call_command('migrate')
    print()

    # Create initial data
    create_superuser()
    create_test_data()
    create_blog_data()
    create_support_resources()

    print("\nDatabase seeding completed!\n")


if __name__ == '__main__':
    main()

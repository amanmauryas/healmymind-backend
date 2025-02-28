import re
from typing import Any, Dict, List
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from .constants import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE,
    MAX_IMAGE_DIMENSIONS
)

def validate_password_strength(password: str) -> None:
    """
    Validate password strength requirements.
    """
    if len(password) < 8:
        raise ValidationError(
            _('Password must be at least 8 characters long.'),
            code='password_too_short'
        )
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _('Password must contain at least one uppercase letter.'),
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _('Password must contain at least one lowercase letter.'),
            code='password_no_lower'
        )
    
    if not re.search(r'[0-9]', password):
        raise ValidationError(
            _('Password must contain at least one number.'),
            code='password_no_number'
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            _('Password must contain at least one special character.'),
            code='password_no_special'
        )

def validate_file_type(file: Any) -> None:
    """
    Validate file type against allowed types.
    """
    if not file.content_type in ALLOWED_FILE_TYPES:
        raise ValidationError(
            _('File type not supported. Allowed types: %(types)s'),
            params={'types': ', '.join(ALLOWED_FILE_TYPES)},
            code='invalid_file_type'
        )

def validate_file_size(file: Any) -> None:
    """
    Validate file size against maximum allowed size.
    """
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            _('File too large. Maximum size is %(max_size)s MB.'),
            params={'max_size': MAX_FILE_SIZE / (1024 * 1024)},
            code='file_too_large'
        )

def validate_image_dimensions(image: Any) -> None:
    """
    Validate image dimensions against maximum allowed dimensions.
    """
    if image.width > MAX_IMAGE_DIMENSIONS[0] or image.height > MAX_IMAGE_DIMENSIONS[1]:
        raise ValidationError(
            _('Image dimensions too large. Maximum dimensions are %(width)sx%(height)s.'),
            params={'width': MAX_IMAGE_DIMENSIONS[0], 'height': MAX_IMAGE_DIMENSIONS[1]},
            code='image_too_large'
        )

def validate_test_answers(answers: Dict[str, Any], questions: List[Dict[str, Any]]) -> None:
    """
    Validate test answers against questions.
    """
    question_ids = {str(q['id']) for q in questions}
    answer_ids = set(answers.keys())

    # Check if all questions are answered
    if question_ids != answer_ids:
        raise ValidationError(
            _('All questions must be answered.'),
            code='incomplete_answers'
        )

    # Validate answer values
    for q_id, answer in answers.items():
        question = next((q for q in questions if str(q['id']) == q_id), None)
        if question:
            valid_values = [opt['value'] for opt in question['options']]
            if answer not in valid_values:
                raise ValidationError(
                    _('Invalid answer value for question %(q_id)s.'),
                    params={'q_id': q_id},
                    code='invalid_answer'
                )

def validate_phone_number(phone: str) -> None:
    """
    Validate phone number format.
    """
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, phone):
        raise ValidationError(
            _('Invalid phone number format.'),
            code='invalid_phone'
        )

def validate_username(username: str) -> None:
    """
    Validate username format.
    """
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
        raise ValidationError(
            _('Username must be 3-30 characters long and contain only letters, numbers, and underscores.'),
            code='invalid_username'
        )

def validate_url(url: str) -> None:
    """
    Validate URL format.
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    if not re.match(pattern, url):
        raise ValidationError(
            _('Invalid URL format.'),
            code='invalid_url'
        )

def validate_date_range(start_date: Any, end_date: Any) -> None:
    """
    Validate date range.
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            _('End date must be after start date.'),
            code='invalid_date_range'
        )

def validate_tags(tags: List[str]) -> None:
    """
    Validate tags format and count.
    """
    if len(tags) > 5:
        raise ValidationError(
            _('Maximum 5 tags allowed.'),
            code='too_many_tags'
        )
    
    for tag in tags:
        if not re.match(r'^[a-zA-Z0-9-]{2,30}$', tag):
            raise ValidationError(
                _('Invalid tag format. Tags must be 2-30 characters and contain only letters, numbers, and hyphens.'),
                code='invalid_tag'
            )

class CustomEmailValidator(EmailValidator):
    """
    Custom email validator with additional checks.
    """
    def __call__(self, value):
        super().__call__(value)
        
        # Additional custom validations
        if value.split('@')[0] in ['admin', 'administrator', 'root', 'system']:
            raise ValidationError(
                _('This email prefix is not allowed.'),
                code='invalid_email_prefix'
            )
        
        # Check for disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.com']  # Add more as needed
        domain = value.split('@')[1]
        if domain in disposable_domains:
            raise ValidationError(
                _('Disposable email addresses are not allowed.'),
                code='disposable_email'
            )

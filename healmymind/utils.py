import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
import openai
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def generate_token(user_id: int, expiry_hours: int = 24) -> str:
    """
    Generate a JWT token for email verification or password reset.
    """
    expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
    payload = {
        'user_id': user_id,
        'exp': expiry
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> Optional[int]:
    """
    Verify a JWT token and return the user_id if valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None

def send_email_template(
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str]
) -> bool:
    """
    Send an email using a template.
    """
    try:
        html_message = render_to_string(template_name, context)
        sent = send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list
        )
        return bool(sent)
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def calculate_test_score(answers: Dict[str, int], test_type: str) -> Dict[str, Any]:
    """
    Calculate test score and determine severity level.
    """
    total_score = sum(answers.values())
    
    # Define scoring ranges for different test types
    scoring_ranges = {
        'PHQ9': [
            {'min': 0, 'max': 4, 'severity': 'MINIMAL'},
            {'min': 5, 'max': 9, 'severity': 'MILD'},
            {'min': 10, 'max': 14, 'severity': 'MODERATE'},
            {'min': 15, 'max': 27, 'severity': 'SEVERE'}
        ],
        'GAD7': [
            {'min': 0, 'max': 4, 'severity': 'MINIMAL'},
            {'min': 5, 'max': 9, 'severity': 'MILD'},
            {'min': 10, 'max': 14, 'severity': 'MODERATE'},
            {'min': 15, 'max': 21, 'severity': 'SEVERE'}
        ]
    }
    
    # Determine severity level
    ranges = scoring_ranges.get(test_type, [])
    severity = 'UNKNOWN'
    for range_info in ranges:
        if range_info['min'] <= total_score <= range_info['max']:
            severity = range_info['severity']
            break
    
    return {
        'score': total_score,
        'severity': severity
    }

async def get_ai_analysis(test_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get AI-powered analysis of test results.
    """
    try:
        prompt = f"""
        Analyze the following mental health test results:
        Test Type: {test_result['test_type']}
        Score: {test_result['score']}
        Severity: {test_result['severity']}
        
        Provide a comprehensive analysis and recommendations.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a mental health analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return {
            'analysis': response.choices[0].message.content,
            'confidence': response.choices[0].finish_reason == 'stop'
        }
    except Exception as e:
        logger.error(f"Error getting AI analysis: {str(e)}")
        return {
            'analysis': "Unable to generate analysis at this time.",
            'confidence': False
        }

def analyze_chat_sentiment(message: str) -> Dict[str, Any]:
    """
    Analyze sentiment of chat messages.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of this message."},
                {"role": "user", "content": message}
            ]
        )
        
        return {
            'sentiment': response.choices[0].message.content,
            'confidence': response.choices[0].finish_reason == 'stop'
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return {
            'sentiment': 'neutral',
            'confidence': 0.0
        }

def format_error_response(error_type: str, message: str) -> Dict[str, Any]:
    """
    Format consistent error responses.
    """
    return {
        'error': {
            'type': error_type,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
    }

def paginate_queryset(queryset: Any, page: int, page_size: int) -> Dict[str, Any]:
    """
    Helper function for consistent pagination.
    """
    start = (page - 1) * page_size
    end = start + page_size
    total = queryset.count()
    
    return {
        'items': queryset[start:end],
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }

def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    """
    from bleach import clean
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'code', 'pre'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    return clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

# healmymind API Documentation

## Base URL
```
Production: https://api.healmymindai.com
Staging: https://api.staging.healmymindai.com
Development: http://localhost:8000
```

## Authentication

### JWT Authentication
```http
POST /api/token/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "your-password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## User Management

### Register User
```http
POST /api/users/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "username": "username",
    "password": "secure-password",
    "password2": "secure-password"
}
```

### Get User Profile
```http
GET /api/users/profile/
Authorization: Bearer <token>
```

### Update Profile
```http
PUT /api/users/profile/update/
Authorization: Bearer <token>
Content-Type: application/json

{
    "bio": "User bio",
    "preferences": {
        "theme": "dark",
        "notifications": true
    }
}
```

## Mental Health Tests

### List Available Tests
```http
GET /api/tests/
Authorization: Bearer <token>
```

Response:
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "phq9",
            "name": "PHQ-9 Depression Screening",
            "description": "Patient Health Questionnaire-9",
            "estimated_time": 5
        }
    ]
}
```

### Get Test Details
```http
GET /api/tests/{test_id}/
Authorization: Bearer <token>
```

### Submit Test
```http
POST /api/tests/{test_id}/submit/
Authorization: Bearer <token>
Content-Type: application/json

{
    "answers": {
        "q1": 2,
        "q2": 1,
        "q3": 0
    }
}
```

### Get Test Results
```http
GET /api/tests/results/{result_id}/
Authorization: Bearer <token>
```

## Blog System

### List Posts
```http
GET /api/blog/posts/
```

Query Parameters:
- `page`: Page number (default: 1)
- `category`: Filter by category
- `tag`: Filter by tag
- `search`: Search term

### Get Post Details
```http
GET /api/blog/posts/{slug}/
```

### Create Comment
```http
POST /api/blog/posts/{slug}/comments/
Authorization: Bearer <token>
Content-Type: application/json

{
    "content": "Great article!",
    "parent": null
}
```

## Chat Support

### Create Conversation
```http
POST /api/chat/conversations/create/
Authorization: Bearer <token>
Content-Type: application/json

{
    "initial_message": "Hello, I need help with..."
}
```

### Send Message
```http
POST /api/chat/conversations/{id}/send/
Authorization: Bearer <token>
Content-Type: application/json

{
    "content": "Your message here"
}
```

### List Conversations
```http
GET /api/chat/conversations/
Authorization: Bearer <token>
```

## Error Responses

### 400 Bad Request
```json
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid input data",
        "details": {
            "field": ["Error message"]
        }
    }
}
```

### 401 Unauthorized
```json
{
    "error": {
        "type": "AuthenticationError",
        "message": "Invalid or expired token"
    }
}
```

### 403 Forbidden
```json
{
    "error": {
        "type": "PermissionDenied",
        "message": "You do not have permission to perform this action"
    }
}
```

### 404 Not Found
```json
{
    "error": {
        "type": "NotFound",
        "message": "Resource not found"
    }
}
```

### 429 Too Many Requests
```json
{
    "error": {
        "type": "RateLimitExceeded",
        "message": "Too many requests",
        "retry_after": 60
    }
}
```

## Rate Limiting

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Admin users: Unlimited requests

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1635724800
```

## Pagination

Query Parameters:
- `page`: Page number
- `page_size`: Items per page (default: 10, max: 100)

Response Format:
```json
{
    "count": 100,
    "next": "https://api.healmymindai.com/endpoint/?page=2",
    "previous": null,
    "results": []
}
```

## Filtering and Sorting

Query Parameters:
- `ordering`: Field to sort by (prefix with - for descending)
- `search`: Search term
- `filters`: Field-specific filters

Example:
```
GET /api/blog/posts/?ordering=-created_at&category=mental-health
```

## Websocket Endpoints

### Chat WebSocket
```
ws://api.healmymindai.com/ws/chat/{conversation_id}/
```

Message Format:
```json
{
    "type": "message",
    "content": "Your message",
    "timestamp": "2024-02-28T12:00:00Z"
}
```

## API Versioning

Include version in header:
```
X-API-Version: 1.0
```

## Questions & Support

- Email: api@healmymindai.com
- Documentation: https://docs.healmymindai.com
- Status Page: https://status.healmymindai.com

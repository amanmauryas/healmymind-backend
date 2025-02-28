"""
ASGI config for healmymind project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import django

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healmymind.settings')

# Initialize Django
django.setup()

# Import websocket URLs after Django setup
from chat.routing import websocket_urlpatterns

class WebSocketCloseHandler:
    """
    Middleware to handle WebSocket connection closing.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            # Add close handler to scope
            scope['websocket_close'] = lambda: None
        return await self.app(scope, receive, send)

class WebSocketLoggingMiddleware:
    """
    Middleware to log WebSocket connections and events.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            # Log connection
            import logging
            logging.info(f"WebSocket connection from {scope['client']}")
            
            # Wrap receive to log messages
            original_receive = receive
            async def receive_wrapper():
                message = await original_receive()
                if message['type'] == 'websocket.receive':
                    logging.info(f"WebSocket message received: {message.get('text', '')}")
                return message
            
            # Wrap send to log messages
            original_send = send
            async def send_wrapper(message):
                if message['type'] == 'websocket.send':
                    logging.info(f"WebSocket message sent: {message.get('text', '')}")
                await original_send(message)
            
            return await self.app(scope, receive_wrapper, send_wrapper)
        return await self.app(scope, receive, send)

class WebSocketRateLimiter:
    """
    Middleware to implement rate limiting for WebSocket connections.
    """
    def __init__(self, app):
        self.app = app
        self.rate_limit = 100  # messages per minute
        self.connections = {}

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            client = scope['client']
            
            # Initialize rate limiting for new client
            if client not in self.connections:
                from collections import deque
                import time
                self.connections[client] = deque(maxlen=self.rate_limit)
            
            # Wrap receive to implement rate limiting
            original_receive = receive
            async def receive_wrapper():
                message = await original_receive()
                if message['type'] == 'websocket.receive':
                    # Check rate limit
                    now = time.time()
                    self.connections[client].append(now)
                    
                    if len(self.connections[client]) == self.rate_limit:
                        oldest = self.connections[client][0]
                        if now - oldest < 60:  # Within one minute
                            # Rate limit exceeded
                            await send({
                                'type': 'websocket.close',
                                'code': 1008,  # Policy violation
                                'reason': 'Rate limit exceeded'
                            })
                            return {'type': 'websocket.disconnect'}
                
                return message
            
            return await self.app(scope, receive_wrapper, send)
        return await self.app(scope, receive, send)

# Initialize the ASGI application
django_asgi_app = get_asgi_application()

# Configure the ASGI application with WebSocket support
application = ProtocolTypeRouter({
    # HTTP requests are handled by Django's ASGI application
    "http": django_asgi_app,
    
    # WebSocket requests are handled by the WebSocket consumer
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            WebSocketRateLimiter(
                WebSocketLoggingMiddleware(
                    WebSocketCloseHandler(
                        URLRouter(websocket_urlpatterns)
                    )
                )
            )
        )
    ),
})

# Error handling middleware
async def error_handler(scope, receive, send):
    """
    Middleware to handle errors in ASGI application.
    """
    try:
        await application(scope, receive, send)
    except Exception as e:
        # Log the error
        import logging
        logging.exception("Error in ASGI application")
        
        if scope['type'] == 'http':
            # Return error response for HTTP requests
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    [b'content-type', b'application/json'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b'{"error": "Internal Server Error"}',
            })
        elif scope['type'] == 'websocket':
            # Close WebSocket connection on error
            await send({
                'type': 'websocket.close',
                'code': 1011,  # Internal error
                'reason': 'Internal server error'
            })

# Wrap application with error handler
application = error_handler

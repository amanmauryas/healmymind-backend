from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from typing import Dict, Any, Optional
from django.db.models.query import QuerySet

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for most API endpoints.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema: Dict) -> Dict:
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?page=4',
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?page=2',
                },
                'results': schema,
            },
        }

class LargeResultsSetPagination(StandardResultsSetPagination):
    """
    Pagination for endpoints that may return larger datasets.
    """
    page_size = 50
    max_page_size = 1000

class SmallResultsSetPagination(StandardResultsSetPagination):
    """
    Pagination for endpoints that return smaller datasets.
    """
    page_size = 5
    max_page_size = 20

class CursorPagination(PageNumberPagination):
    """
    Cursor-based pagination for better performance with large datasets.
    """
    page_size = 20
    cursor_query_param = 'cursor'
    ordering = '-created_at'

    def paginate_queryset(self, queryset: QuerySet, request: Any, view: Optional[Any] = None) -> QuerySet:
        self.cursor = request.query_params.get(self.cursor_query_param)
        if self.cursor:
            # Implement cursor-based filtering based on your needs
            created_at = self.decode_cursor(self.cursor)
            queryset = queryset.filter(created_at__lt=created_at)
        return super().paginate_queryset(queryset[:self.page_size + 1], request, view)

    def get_paginated_response(self, data: Any) -> Response:
        next_cursor = None
        if len(data) > self.page_size:
            next_cursor = self.encode_cursor(data[-2]['created_at'])
            data = data[:-1]

        return Response(OrderedDict([
            ('next_cursor', next_cursor),
            ('results', data)
        ]))

    def encode_cursor(self, timestamp: str) -> str:
        """
        Encode a timestamp into a cursor string.
        """
        import base64
        return base64.b64encode(str(timestamp).encode()).decode()

    def decode_cursor(self, cursor: str) -> str:
        """
        Decode a cursor string back into a timestamp.
        """
        import base64
        return base64.b64decode(cursor.encode()).decode()

class InfinitePagination(PageNumberPagination):
    """
    Pagination for infinite scroll implementations.
    """
    page_size = 20
    max_page_size = 50

    def get_paginated_response(self, data: Any) -> Response:
        return Response({
            'has_more': self.page.has_next(),
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'results': data
        })

class CustomPagination:
    """
    Custom pagination helper for manual pagination needs.
    """
    @staticmethod
    def get_paginated_response(queryset: QuerySet, page: int, page_size: int) -> Dict[str, Any]:
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': queryset[start:end],
            'has_next': end < total,
            'has_previous': page > 1
        }

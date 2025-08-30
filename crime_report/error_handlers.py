from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def handle_404(request, exception):
    """Handle 404 Not Found errors."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Resource not found',
            'status_code': 404
        }, status=404)
    return render(request, 'crime_report/errors/404.html', status=404)

def handle_500(request):
    """Handle 500 Internal Server Error."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal server error',
            'status_code': 500
        }, status=500)
    return render(request, 'crime_report/errors/500.html', status=500)

def handle_403(request, exception):
    """Handle 403 Forbidden errors."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Access forbidden',
            'status_code': 403
        }, status=403)
    return render(request, 'crime_report/errors/403.html', status=403)

def handle_400(request, exception):
    """Handle 400 Bad Request errors."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Bad request',
            'status_code': 400
        }, status=400)
    return render(request, 'crime_report/errors/400.html', status=400)
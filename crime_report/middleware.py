from django.http import HttpResponseForbidden
from django.conf import settings
import re
import time

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check for suspicious SQL injection patterns
        if self._has_sql_injection(request):
            return HttpResponseForbidden('Forbidden')
        
        # Check for suspicious file paths
        if self._has_path_traversal(request):
            return HttpResponseForbidden('Forbidden')
        
        # Check file upload size
        if request.method == 'POST' and request.FILES:
            for uploaded_file in request.FILES.values():
                if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
                    return HttpResponseForbidden('File too large')
        
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    
    def _has_sql_injection(self, request):
        """Check for common SQL injection patterns"""
        sql_patterns = [
            r'(\s|\'|\"|\d|\W)+((UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE)\s)',
            r'(\s|\'|\"|\d|\W)+(OR|AND)(\s|\d|\W)+(\d|\w|\W)+(\=|\>|\<)',
        ]
        
        for pattern in sql_patterns:
            for param in request.GET.values():
                if re.search(pattern, param, re.IGNORECASE):
                    return True
            if request.method == 'POST':
                for param in request.POST.values():
                    if re.search(pattern, param, re.IGNORECASE):
                        return True
        return False
    
    def _has_path_traversal(self, request):
        """Check for path traversal attempts"""
        path = request.path_info
        if '../' in path or '..\\' in path:
            return True
        return False

class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if session has expired
            if 'last_activity' in request.session:
                last_activity = request.session['last_activity']
                if time.time() - last_activity > settings.SESSION_COOKIE_AGE:
                    from django.contrib.auth import logout
                    logout(request)
            
            # Update last activity time
            request.session['last_activity'] = time.time()
        
        response = self.get_response(request)
        return response
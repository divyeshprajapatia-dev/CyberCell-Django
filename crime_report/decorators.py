from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def police_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['police', 'admin']:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def can_view_report(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        report_id = kwargs.get('pk')
        if not report_id:
            raise PermissionDenied
        
        from .models import CrimeReport
        report = CrimeReport.objects.get(pk=report_id)
        
        if not report.can_view_details(request.user):
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('crime_list')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

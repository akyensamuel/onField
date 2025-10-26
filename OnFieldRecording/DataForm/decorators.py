"""
Custom decorators for permission and access control
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Operation


def staff_required(view_func):
    """
    Decorator to ensure user is logged in and has staff or admin role.
    Checks UserProfile.role field.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found. Please contact administrator.")
            return redirect('login')
        
        # Both staff and admin roles are allowed
        if request.user.profile.role in ['staff', 'admin']:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "You don't have permission to access this page.")
        return HttpResponseForbidden("Access Denied: Staff access required")
    
    return wrapper


def admin_required(view_func):
    """
    Decorator to ensure user is logged in and has admin role.
    Only users with UserProfile.role = 'admin' can access.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found. Please contact administrator.")
            return redirect('login')
        
        if request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "You don't have permission to access this page. Admin access required.")
        return HttpResponseForbidden("Access Denied: Admin access required")
    
    return wrapper


def active_operation_required(view_func):
    """
    Decorator to ensure there is an active operation.
    Used for views that require an active operation (like creating records).
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        active_operation = Operation.objects.filter(is_active=True, is_deleted=False).first()
        
        if not active_operation:
            messages.warning(
                request, 
                "No active operation found. Please contact an administrator to activate an operation."
            )
            # Redirect admins to operation list, staff to dashboard
            if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
                return redirect('operation_list')
            else:
                return redirect('dashboard')
        
        # Attach active operation to request for easy access in view
        request.active_operation = active_operation
        return view_func(request, *args, **kwargs)
    
    return wrapper


def staff_can_edit_record(view_func):
    """
    Decorator to check if staff can edit a specific record.
    Staff can only edit their own records in active operations.
    Admins can edit any record.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from .models import Record
        
        # Get record_id from kwargs or args
        record_id = kwargs.get('pk') or kwargs.get('record_id')
        
        if not record_id:
            messages.error(request, "Record ID not provided.")
            return redirect('record_list')
        
        try:
            record = Record.objects.get(pk=record_id)
        except Record.DoesNotExist:
            messages.error(request, "Record not found.")
            return redirect('record_list')
        
        # Admins can edit any record
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        
        # Staff can only edit their own records
        if record.created_by != request.user:
            messages.error(request, "You can only edit records you created.")
            return HttpResponseForbidden("Access Denied: You can only edit your own records")
        
        # Staff cannot edit records in closed operations
        if not record.operation.is_active:
            messages.error(request, "Cannot edit records in closed operations.")
            return HttpResponseForbidden("Access Denied: Operation is closed")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def superuser_required(view_func):
    """
    Decorator to ensure user is a superuser.
    Used for critical administrative functions.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "You must be a superuser to access this page.")
        return HttpResponseForbidden("Access Denied: Superuser access required")
    
    return wrapper

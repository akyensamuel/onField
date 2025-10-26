"""
Django signals for automatic model creation and audit logging
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile, Operation, Record, AuditLog, RecordMedia
import json


# =============================================
# USER PROFILE AUTO-CREATION
# =============================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile whenever User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


# =============================================
# AUDIT LOGGING SIGNALS
# =============================================

def get_client_ip(request=None):
    """Extract client IP from request"""
    if request is None:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Store previous values for detecting changes
_operation_pre_save_cache = {}
_record_pre_save_cache = {}


@receiver(pre_save, sender=Operation)
def cache_operation_state(sender, instance, **kwargs):
    """Cache the previous state before saving"""
    if instance.pk:
        try:
            old_instance = Operation.objects.get(pk=instance.pk)
            _operation_pre_save_cache[instance.pk] = {
                'is_active': old_instance.is_active,
                'is_deleted': old_instance.is_deleted,
            }
        except Operation.DoesNotExist:
            pass


@receiver(post_save, sender=Operation)
def log_operation_changes(sender, instance, created, **kwargs):
    """Log operation creation and significant changes"""
    from threading import current_thread
    
    # Try to get request from thread local storage (if middleware is set up)
    request = getattr(current_thread(), 'request', None)
    user = getattr(current_thread(), 'user', None)
    ip_address = get_client_ip(request) if request else None
    
    if created:
        # Operation created
        AuditLog.objects.create(
            user=instance.created_by,
            action_type='create',
            target_type='operation',
            target_id=instance.id,
            details={
                'name': instance.name,
                'description': instance.description,
                'is_active': instance.is_active,
            },
            ip_address=ip_address
        )
    else:
        # Check for significant changes
        old_state = _operation_pre_save_cache.pop(instance.pk, {})
        
        # Check if operation was closed
        if old_state.get('is_active') and not instance.is_active:
            AuditLog.objects.create(
                user=instance.closed_by or user,
                action_type='close_operation',
                target_type='operation',
                target_id=instance.id,
                details={
                    'name': instance.name,
                    'closed_at': str(instance.closed_at),
                },
                ip_address=ip_address
            )
        
        # Check if operation was reopened
        elif not old_state.get('is_active') and instance.is_active:
            AuditLog.objects.create(
                user=user,
                action_type='reopen_operation',
                target_type='operation',
                target_id=instance.id,
                details={
                    'name': instance.name,
                },
                ip_address=ip_address
            )


@receiver(post_delete, sender=Operation)
def log_operation_delete(sender, instance, **kwargs):
    """Log operation deletion"""
    from threading import current_thread
    
    request = getattr(current_thread(), 'request', None)
    user = getattr(current_thread(), 'user', None)
    ip_address = get_client_ip(request) if request else None
    
    AuditLog.objects.create(
        user=user,
        action_type='delete',
        target_type='operation',
        target_id=instance.id,
        details={
            'name': instance.name,
        },
        ip_address=ip_address
    )


@receiver(pre_save, sender=Record)
def cache_record_state(sender, instance, **kwargs):
    """Cache the previous state before saving"""
    if instance.pk:
        try:
            old_instance = Record.objects.get(pk=instance.pk)
            _record_pre_save_cache[instance.pk] = {
                'status': old_instance.status,
                'customer_name': old_instance.customer_name,
                'meter_reading': str(old_instance.meter_reading),
            }
        except Record.DoesNotExist:
            pass


@receiver(post_save, sender=Record)
def log_record_changes(sender, instance, created, **kwargs):
    """Log record creation and updates"""
    from threading import current_thread
    
    request = getattr(current_thread(), 'request', None)
    user = getattr(current_thread(), 'user', None) or instance.created_by
    ip_address = get_client_ip(request) if request else None
    
    if created:
        # Record created
        AuditLog.objects.create(
            user=user,
            action_type='create',
            target_type='record',
            target_id=instance.id,
            details={
                'record_number': instance.record_number,
                'operation': instance.operation.name,
                'customer_name': instance.customer_name,
                'status': instance.status,
            },
            ip_address=ip_address
        )
    else:
        # Record updated
        old_state = _record_pre_save_cache.pop(instance.pk, {})
        changes = {}
        
        if old_state.get('status') != instance.status:
            changes['status'] = {'old': old_state.get('status'), 'new': instance.status}
        
        if changes:
            AuditLog.objects.create(
                user=user,
                action_type='update',
                target_type='record',
                target_id=instance.id,
                details={
                    'record_number': instance.record_number,
                    'changes': changes,
                },
                ip_address=ip_address
            )


@receiver(post_delete, sender=Record)
def log_record_delete(sender, instance, **kwargs):
    """Log record deletion"""
    from threading import current_thread
    
    request = getattr(current_thread(), 'request', None)
    user = getattr(current_thread(), 'user', None)
    ip_address = get_client_ip(request) if request else None
    
    AuditLog.objects.create(
        user=user,
        action_type='delete',
        target_type='record',
        target_id=instance.id,
        details={
            'record_number': instance.record_number,
            'customer_name': instance.customer_name,
        },
        ip_address=ip_address
    )


@receiver(post_save, sender=RecordMedia)
def log_media_upload(sender, instance, created, **kwargs):
    """Log media file uploads"""
    from threading import current_thread
    
    if created:
        request = getattr(current_thread(), 'request', None)
        user = instance.uploaded_by
        ip_address = get_client_ip(request) if request else None
        
        AuditLog.objects.create(
            user=user,
            action_type='create',
            target_type='media',
            target_id=instance.id,
            details={
                'record_number': instance.record.record_number,
                'file_size': instance.file_size,
            },
            ip_address=ip_address
        )

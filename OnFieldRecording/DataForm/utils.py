"""
Utility functions for DataForm app
"""

from django.db import transaction
from .models import Operation


def generate_record_number(operation):
    """
    Generate a unique record number for a given operation.
    Format: JOB-{operation_id:03d}-{sequence:04d}
    Example: JOB-001-0042
    
    Uses select_for_update() to prevent race conditions.
    
    Args:
        operation: Operation instance
    
    Returns:
        str: Formatted record number
    
    Raises:
        Operation.DoesNotExist: If operation doesn't exist
    """
    with transaction.atomic():
        # Lock the operation row to prevent concurrent updates
        op = Operation.objects.select_for_update().get(pk=operation.pk)
        
        # Generate the record number
        record_number = f"JOB-{op.id:03d}-{op.next_record_seq:04d}"
        
        # Increment the sequence for next record
        op.next_record_seq += 1
        op.save(update_fields=['next_record_seq'])
        
        return record_number


def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
    
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))


def calculate_gps_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
    
    Returns:
        float: Distance in kilometers
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def get_client_ip_from_request(request):
    """
    Get client IP address from Django request.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

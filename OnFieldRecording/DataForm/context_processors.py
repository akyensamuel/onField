"""
Context processors for DataForm app
These make data available to all templates automatically
"""

from .models import Operation


def active_operation(request):
    """
    Add the active operation to all template contexts
    This makes {{ active_operation }} available in all templates
    """
    if request.user.is_authenticated:
        active_op = Operation.objects.filter(is_active=True, is_deleted=False).first()
        return {'active_operation': active_op}
    return {'active_operation': None}
